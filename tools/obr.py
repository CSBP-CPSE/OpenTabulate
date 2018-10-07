"""
This module defines the OpenBusinessRepository API, which contains classes and
methods for a data processing production system. In abstraction, Source objects
are created to represent everything about a dataset, such as its metadata and 
references to its location. The modification of Source objects by DataProcess 
objects represents this idea of the data being processed, cleaned, and formatted. 
A DataProcess object uses the Algorithm class methods and its child classes to 
perform the necessary data processing.

Created and written by Maksym Neyra-Nesterenko.

------------------------------------
Data Exploration and Integration Lab
Center for Special Business Projects
Statistics Canada
------------------------------------
"""

###########
# MODULES #
###########

import operator
import os
import json
import csv
from xml.etree import ElementTree
import re
import urllib.request


#############################
# CORE DATA PROCESS CLASSES #
#############################

class DataProcess(object):
    """
    A data processing interface for a source file.

    Attributes:

      source: A dataset and its associated metadata, defined as a Source 
        object.

      postal_address_parser: An object containing an address parser method,
        defined by an AddressParser object.
    """
    def __init__(self, source, address_parser):
        """
        Initialize a DataProcess object.

        Args:
        
          source: A dataset and its associated metadata, defined
            as a Source object.

          address_parser: An address parsing function which accepts a
            string as an argument.
        """
        self.source = source
        self.postal_address_parser = AddressParser(address_parser)

    def process(self):
        """
        Process a data set using methods from Algorithm.
        """
        if self.source.metadata['format'] == 'csv':
            fmtproc = Process_CSV(self.postal_address_parser.parse)
            fmtproc.format_correction(self.source, fmtproc.char_encode_check(self.source))
        elif self.source.metadata['format'] == 'xml':
            fmtproc = Process_XML(self.postal_address_parser.parse)
        fmtproc.extract_labels(self.source) 
        fmtproc.parse(self.source)
        fmtproc.clean(self.source)
        

class AddressParser(object):
    """
    Wrapper class for an address parser.

    Currently supported parsers: libpostal

    Attributes:

      address_parser: Address parsing function.
    """
    def __init__(self, address_parser):
        """
        Initialize an AddressParser object.

        Args:

          address_parser: An address parsing function which accepts a string 
            as an argument.
        """
        self.address_parser = address_parser

    def parse(self, addr):
        """
        Parses and address string and returns the tokens.

        Args:

          addr: A string containing the address to parse.
        """
        return self.address_parser(addr)


#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm(object):
    """
    Parent algorithm class for data processing.

    Attributes:

      FIELD_LABEL: Standardized field names.

      ADDR_FIELD_LABEL: Standardized address field names.

      FORCE_LABEL: Field names acceptable by 'force' tag.

      ENCODING_LIST: List of character encodings to test.

      address_parser: Address parsing function to use.
    """
    FIELD_LABEL = ['bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc', \
                    'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active', \
                    'full_addr', \
                    'house_number', 'road', 'postcode', 'unit', 'city', 'prov', 'country', \
                    'phone', 'fax', 'email', 'website', 'tollfree',\
                    'comdist', 'region', \
                    'longitude', \
                    'latitude', \
                    'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',\
                    'home_bus', 'munic_bus', 'nonres_bus', \
                    'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3', \
                    'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6', \
                    'naics_desc', \
                    'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2', \
                    'facebook', 'twitter', 'linkedin', 'youtube', 'instagram']


    ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'prov', 'country', 'postcode']

    FORCE_LABEL = ['city', 'prov', 'country']

    ENCODING_LIST = ["utf-8", "cp1252", "cp437"]

    _ADDR_LABEL_TO_POSTAL = {'house_number' : 'house_number', \
                            'road' : 'road', \
                            'unit' : 'unit', \
                            'city' : 'city', \
                            'prov' : 'state', \
                            'country' : 'country', \
                            'postcode' : 'postcode' }


    def __init__(self, address_parser):
        """
        Initializes Algorithm object.

        Args:
          address_parser: Address parsing function.
        """
        self.address_parser = address_parser
    
    def char_encode_check(self, source):
        """
        Identifies the character encoding of a source by reading the metadata
        or by a heuristic test.
        
        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.

        Returns:

          e: the character encoding as described by Python as a string.

        Raises:

          ValueError: Invalid encoding specified in source file.

          RunTimeError: Character encoding test failed.
        """
        metadata = source.metadata
        if 'encoding' in metadata:
            data_enc = metadata.data['encoding']
            if data_enc in self.ENCODING_LIST:
                return data_enc
            else:
                raise ValueError(data_enc + " is not a valid encoding.")
        else:
            for e in self.ENCODING_LIST:
                try:
                    with open('./pddir/raw/' + metadata['file'], encoding=e) as f:
                        for line in f:
                            pass
                    return e
                except UnicodeDecodeError:
                    pass
            raise RuntimeError("Could not guess original character encoding.")


    ############################################
    # Support functions for the 'parse' method #
    ############################################

    def _isRowEmpty(self, r):
        """
        Checks if a list 'r' consists of only empty string entries.
        """
        for e in r:
            if e != "":
                return False
        return True

    def _quick_scrub(self, entry):
        """
        Cleans a string 'entry' using regular expressions and returns it.
        """
        if isinstance(entry, bytes):
            entry = entry.decode()
        # remove [:space:] char class
        #
        # since this includes removal of newlines, the next regexps are safe and
        # do not require the "DOTALL" flag
        entry = re.sub(r"\s+", " ", entry)
        # remove spaces occuring at the beginning and end of an entry
        entry = re.sub(r"^\s+([^\s].+)", r"\1", entry)
        entry = re.sub(r"(.+[^\s])\s+$", r"\1", entry)
        entry = re.sub(r"^\s+$", "", entry)
        # make entries lowercase
        entry = entry.lower()
        return entry

    def blank_fill(self, source):
        """
        Adds columns excluded by original data processing/metadata to a 
        formatted dataset and fills entries with blanks.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        LABELS = [i for i in self.FIELD_LABEL if i != "full_addr"]

        # open files for read and writing
        f = open(source.cleanpath, 'r')
        blank_fill_f = open(source.cleanpath + '-temp', 'w')

        # initialize csv reader/writer
        rf = csv.DictReader(f)
        wf = csv.writer(blank_fill_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        wf.writerow(LABELS)

        for old_row in rf:
            row2write = []
            for col in LABELS:
                if col not in old_row:
                    row2write.append("")
                else:
                    row2write.append(old_row[col])
            wf.writerow(row2write)

        blank_fill_f.close()
        f.close()
        os.rename(source.cleanpath + '-temp', source.cleanpath)

    
class Process_CSV(Algorithm):
    """
    A child class of Algorithm, accompanied with methods designed for
    CSV-formatted datasets.
    """
    
    def extract_labels(self, source):
        """
        Constructs a dictionary that stores only tags that were exclusively used in 
        a source file.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        metadata = source.metadata
        label_map = dict()
        for i in self.FIELD_LABEL:
            if i in metadata['info'] and (not (i in self.ADDR_FIELD_LABEL)):
                label_map[i] = metadata['info'][i]
            elif ('address' in metadata['info']) and (i in metadata['info']['address']):
                AddressVarField = metadata['info']['address'][i]
                label_map[i] = AddressVarField
            elif ('force' in metadata) and (i in metadata['force']):
                label_map[i] = 'DPIFORCE'
        source.label_map = label_map


    def parse(self, source):
        """
        Parses a dataset in CSV format to transform into a standardized CSV format.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        if not hasattr(source, 'label_map'):
            raise ValueError("Source object missing 'label_map', 'extract_labels' was not ran.")

        filename = source.metadata['file']
        tags = source.label_map
        enc = self.char_encode_check(source)
        csv_file_read = open(source.dirtypath, 'r', encoding=enc, newline='') # errors='ignore'
        cparse = csv.DictReader(csv_file_read)

        csv_file_write = open(source.dirtypath + '-temp', 'w')
        cprint = csv.writer(csv_file_write, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # write the initial row which identifies each column
        first_row = [f for f in tags]
        if "full_addr" in first_row:
            ind = first_row.index("full_addr")
            first_row.pop(ind)
            for af in reversed(self.ADDR_FIELD_LABEL):
                first_row.insert(ind, af)
        cprint.writerow(first_row)
        try:
            for entity in cparse:
                row = []
                for key in tags:
                    # if key has a JSON array as a value
                    if isinstance(tags[key], list) and key not in self.FORCE_LABEL:
                        entry = ''
                        for i in tags[key]:
                            entry += entity[i] + ' '
                        entry = self._quick_scrub(entry)
                        # if key is full_addr and a JSON array
                        if key != "full_addr":
                            row.append(entry)
                            continue
                        else:
                            ap = self.address_parser(entry)
                            for af in self.ADDR_FIELD_LABEL:
                                if self._ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                                    ind = list(map(operator.itemgetter(1), ap)).index(self._ADDR_LABEL_TO_POSTAL[af])
                                    row.append(ap[ind][0])
                                else:
                                    row.append("")
                            continue
                        # otherwise ...
                    if tags[key] != 'DPIFORCE':
                        entry = self._quick_scrub(entity[tags[key]])
                    else:
                        entry = self._quick_scrub(json_data['force'][key])
                    row.append(entry)
                if not self._isRowEmpty(row):
                    cprint.writerow(row)
        except KeyError:
            print("[E] '", tags[key], "' is not a field name in the CSV file.", sep='')
            csv_file_read.close()
            csv_file_write.close()
        # success
        csv_file_read.close()
        csv_file_write.close()
        os.rename(source.dirtypath + '-temp', source.dirtypath)

    def format_correction(self, source, data_encoding):
        """
        Corrects CSV datasets that possess rows with a number of entries not
        agreeing with the total number of columns. Additionally removes a
        byte order mark if it exists.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.

          data_encoding: The character encoding of the data.
        """
        raw = open(source.rawpath, 'r', encoding=data_encoding)
        dirty = open(source.dirtypath, 'w')
        reader = csv.reader(raw)
        writer = csv.writer(dirty)
        flag = False
        size = 0
        first_row = True
        for row in reader:
            if first_row == True:
                row[0] = re.sub(r"^\ufeff(.+)", r"\1", row[0])
                first_row = False
            if flag == True:
                while len(row) < size:
                    row.append("")
                writer.writerow(row)
            else:
                size = len(row)
                flag = True
                writer.writerow(row)
        raw.close()
        dirty.close()

        
    def clean(self, source):
        """
        A general dataset cleaning method. (May be moved to Algorithm)

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        # DEBUG ###########
        os.rename(source.dirtypath, source.cleanpath)

    

class Process_XML(Algorithm):
    """
    A child class of Algorithm, accompanied with methods designed for
    XML-formatted datasets.
    """

    def extract_labels(self, source):
        """
        Constructs a dictionary that stores only tags that were exclusively used in 
        a source file. Since datasets in XML format will need a header tag in its
        source file, the labels must be use XPath expressions.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        metadata = source.metadata
        label_map = dict()
        # append existing data using XPath expressions (for parsing)
        for i in self.FIELD_LABEL:
            if i in metadata['info'] and (not (i in self.ADDR_FIELD_LABEL)) and i != 'address':
                if isinstance(metadata['info'][i], list):
                    label_map[i] = []
                    for t in metadata['info'][i]:
                        label_map[i].append(".//" + t)
                else:
                    label_map[i] = ".//" + metadata['info'][i]
            # short circuit evaluation
            elif ('address' in metadata['info']) and (i in metadata['info']['address']):
                XPathString = ".//" + metadata['info']['address'][i]
                label_map[i] = XPathString
            elif ('force' in metadata) and (i in metadata['force']):
                label_map[i] = 'DPIFORCE'
        source.label_map = label_map


    def parse(self, source):
        """
        Parses a dataset in XML format to transform into a standardized CSV format.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        if not hasattr(source, 'label_map'):
            raise ValueError("Source object missing 'label_map', 'extract_labels' was not ran.")

        filename = source.metadata['file']
        tags = source.label_map
        header = source.metadata['header']
        enc = self.char_encode_check(source)
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(source.rawpath, parser=xmlp)
        root = tree.getroot()

        csvfile = open(source.dirtypath, 'w')
        cprint = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # write the initial row which identifies each column
        first_row = [f for f in tags]
        if "full_addr" in first_row:
            ind = first_row.index("full_addr")
            first_row.pop(ind)
            for af in reversed(self.ADDR_FIELD_LABEL):
                first_row.insert(ind, af)
        cprint.writerow(first_row)

        for element in root.iter(header):
            row = []
            for key in tags:
                if isinstance(tags[key], list) and key not in self.FORCE_LABEL:
                    entry = ''
                    for i in tags[key]:
                        subelement = element.find(i)
                        subelement = self._xml_empty_element_handler(subelement)
                        entry += subelement + ' '
                    entry = self._quick_scrub(entry)
                    if key != "full_addr":
                        row.append(entry)
                        continue
                    else:
                        ap = self.address_parser(entry)
                        for af in self.ADDR_FIELD_LABEL:
                            if self._ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                                ind = list(map(operator.itemgetter(1), ap)).index(self._ADDR_LABEL_TO_POSTAL[af])
                                row.append(ap[ind][0])
                            else:
                                row.append("")
                        continue
                if key == "full_addr":
                    entry = element.find(tags[key])
                    entry = self._xml_empty_element_handler(entry)
                    entry = self._quick_scrub(entry)
                    ap = self.address_parser(entry)
                    for af in self.ADDR_FIELD_LABEL:
                        if self._ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                            ind = list(map(operator.itemgetter(1), ap)).index(self._ADDR_LABEL_TO_POSTAL[af])
                            row.append(ap[ind][0])
                        else:
                            row.append("")
                    continue
                # otherwise ...
                if tags[key] != 'DPIFORCE':
                    subelement = element.find(tags[key])
                    subel_content = self._xml_empty_element_handler(subelement)
                    row.append(self._quick_scrub(subel_content))
                else:
                    row.append(self._quick_scrub(json_data['force'][key]))
            if not self._isRowEmpty(row):
                cprint.writerow(row)
        csvfile.close()


    def clean(self, source):
        """
        A general dataset cleaning method. (May be moved to Algorithm)

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        # DEBUG ###########
        os.rename(source.dirtypath, source.cleanpath)


    def _xml_empty_element_handler(self, element):
        """
        The 'xml.etree' module returns 'None' for text of empty-element tags. Moreover, 
        if the element cannot be found, the element is 'None'. This function is defined 
        to handle these cases.

        Args:

          element: A node in the XML tree.

        Returns:

          '': missing or empty tag
                  
          element.text: tag text
        """
        if element is None:
            return ''
        if not (element.text is None):
            return element.text
        else:
            return ''



###############################
# SOURCE DATASET / FILE CLASS #
###############################

class Source(object):
    """
    Source dataset class. Contains metadata and other information about the dataset
    and its dirty and clean copies.

    Attributes:
    
      srcpath: path to source file relative to the OBR directory.

      rawpath: path to the raw dataset relative to the OBR directory. This is
        assigned './pddir/raw'.

      dirtypath: path to the dirty dataset relative to the OBR directory. This is
        assigned './pddir/dirty'.

      cleanpath: path to the clean dataset relative to the OBR directory. This is
        assigned './pddir/clean'.
      dirtypath:

      label_map: a dict object that stores the mapping of OBRs standardized labels
        to the dataset's labels, as obtained by the source file.
    """
    def __init__(self, path):
        """
        Initializes a new source file object.

        Raises:
        
          OSError: Path to source file does not exist.
        """
        if not os.path.exists(path):
            raise OSError('Path "%s" does not exist.' % path)
        self.srcpath = path
        with open(path) as f:
            self.metadata = json.load(f)
        self.rawpath = None
        self.dirtypath = None
        self.cleanpath = None
        self.label_map = None
        

    def parse(self):
        """
        Parses the source file to check correction of syntax.

        Raises:

          LookupError: Associated with a missing tag.

          ValueError: Associated with an incorrect entry or combination or entries.
            For example, having an 'address' and 'full_addr' tag will raise this
            error since they cannot both be used in a source file.

          TypeError: Associated with an incorrect JSON type for a tag.
        """
        # required tags
        if 'format' not in self.metadata:
            raise LookupError("'format' tag is missing.")
        if 'file' not in self.metadata:
            raise LookupError("'file' tag is missing.")
        if 'info' not in self.metadata:
            raise LookupError("info' tag is missing.")

        # require tag types
        if not isinstance(self.metadata['format'], str):
            raise TypeError("'format' must be a string.")
        if not isinstance(self.metadata['file'], str):
            raise TypeError("'file' must be a string.")
        if not isinstance(self.metadata['info'], dict):
            raise TypeError("'info' must be an object.")

        # required formats
        if (self.metadata['format'] != 'xml') and (self.metadata['format'] != 'csv'):
            raise ValueError("Unsupported data format '" + self.metadata['format'] + "'")

        # required header if format is not csv
        if (self.metadata['format'] != 'csv') and ('header' not in self.metadata):
            raise LookupError("'header' tag missing for format " + self.metadata['format'])

        if (self.metadata['format'] != 'csv') and ('header' in self.metadata) and (not isinstance(self.metadata['header'], str)):
            raise TypeError("'header' must be a string.")

        # url
        if 'url' in self.metadata and (not isinstance(self.metadata['url'], str)):
            raise TypeError("'url' must be a string.")


        # check that both full_addr and address are not in the source file
        if ('address' in self.metadata['info']) and ('full_addr' in self.metadata['info']):
            raise ValueError("Cannot have both 'full_addr' and 'address' tags in source file.")

        # verify address is an object with valid tags
        if 'address' in self.metadata['info']:
            if not (isinstance(self.metadata['info']['address'], dict)):
                raise TypeError("'address' tag must be an object.")

            for i in self.metadata['info']['address']:
                if not (i in Algorithm.ADDR_FIELD_LABEL):
                    raise ValueError("'address' tag contains an invalid key.")

        # verify force is an object with valid tags
        if 'force' in self.metadata:
            if not (isinstance(self.metadata['force'], dict)):
                raise TypeError("'force' tag must be an object.")

            for i in self.metadata['force']:
                if not (i in Algorithm.FORCE_LABEL):
                    raise ValueError("'force' tag contains an invalid key.")
                elif ('address' in self.metadata['info']) and (i in self.metadata['info']['address']):
                    raise ValueError("Key '", i, "' appears in 'force' and 'address'.")

        # Set rawpath, dirtypath, and cleanpath values
        fname = self.metadata['file']
        self.rawpath = './pddir/raw/' + fname
        if len(fname.split('.')) == 1:
            self.dirtypath = './pddir/dirty/' + fname + "-dirty.csv"
        else:
            self.dirtypath = './pddir/dirty/' + '.'.join(str(x) for x in fname.split('.')[:-1]) + "-dirty.csv"

        if len(fname.split('.')) == 1:
            self.cleanpath = './pddir/clean/' + fname + "-clean.csv"
        else:
            self.cleanpath = './pddir/clean/' + '.'.join(str(x) for x in fname.split('.')[:-1]) + "-clean.csv"
        

    def fetch_url(self):
        """
        Downloads a dataset by fetching its URL and writing to the raw directory.
        """
        response = urllib.request.urlopen(self.metadata['url'])
        bytedata = response.read()
        with open('./pddir/raw/' + self.metadata['file'], 'wb') as data_file:
            data_file.write(bytedata)

    def raw_data_exists(self):
        """
        Checks if raw dataset exists in the required directory.

        Raises:

          OSError: Missing dataset in raw folder.
        """
        if not path.exists('./pddir/raw/' + self.metadata['file']):
            raise OSError("'" + self.metadata['file'] + "' not found in raw folder.")


######################
# OBR.PY DEBUG BLOCK #
######################

if __name__ == "__main__":
    from postal.parser import parse_address
    s = Source('./sources/misc/msbregistry.json')
    s.parse()
    d = DataProcess(s, parse_address)
    d.process()
    
