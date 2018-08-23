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
    Data processing class.
    """
    def __init__(self, source, address_parser):
        self.source = source
        self.postal_address_parser = AddressParser(address_parser)

    def process(self): # DEBUG # May need to update method parameters #
        if self.source.metadata['format'] == 'csv':
            fmtproc = Process_CSV(self.postal_address_parser.parse) 
        elif self.source.metadata['format'] == 'xml':
            fmtproc = Process_XML(self.postal_address_parser.parse)
        fmtproc.extract_labels(self.source) 
        fmtproc.parse(self.source)
#        fmtproc.clean()
        

class AddressParser(object):
    """
    Wrapper class for libpostal.
    Performs output formatting here.
    """
    def __init__(self, address_parser):
        self.address_parser = address_parser

    def parse(self, addr):
        return self.address_parser(addr)


#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm(object):
    """
    Parent algorithm class for data processing.
    """
    # Standardized column names for source files - for usage and
    # documentation, see 'docs/CONTRIB.md' in the repository
    _FIELD_LABEL = ['bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc', \
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


    # Address fields
    _ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'prov', 'country', 'postcode']

    # Labels for the 'force' tag
    _FORCE_LABEL = ['city', 'prov', 'country']

    # Column order, keys expressed as libpostal parser labels
    _ADDR_LABEL_TO_POSTAL = {'house_number' : 'house_number', \
                            'road' : 'road', \
                            'unit' : 'unit', \
                            'city' : 'city', \
                            'prov' : 'state', \
                            'country' : 'country', \
                            'postcode' : 'postcode' }

    # Character encoding list
    _ENCODING_LIST = ["utf-8", "cp1252", "cp437"]

    def __init__(self, address_parser):
        self.address_parser = address_parser.parser
    
    def char_encode_check(self, source):
        metadata = source.metadata
        if 'encoding' in metadata:
            data_enc = metadata.data['encoding']
            if data_enc in self._ENCODING_LIST:
                return data_enc
            else:
                raise ValueError(data_enc + " is not a valid encoding.")
        else:
            for e in self._ENCODING_LIST:
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
        for e in r:
            if e != "":
                return False
        return True

    def _quick_scrub(self, entry):
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
        # DEBUG -- --
        # add regex to handle " entries " like this (remove side spaces)

        # make entries lowercase
        entry = entry.lower()
        return entry

    
class Process_CSV(Algorithm):
    """
    Child class of algorithm.
    """
    def extract_labels(self):
        pass

    def parse(self):
        pass

    def clean(self):
        pass

    

class Process_XML(Algorithm):
    """
    Child class of algorithm.
    """
    def __init__(self, address_parse_func):
        self.address_parser = address_parse_func
    
    def extract_labels(self, source):
        """
        Constructs a dictionary that stores only tags that were exclusively used in 
        a source file. This function is specific to the XML format since it returns 
        a header tag and uses XPath expressions.

        Note:
            N/A

        Args:
            source: a Source object.
        """
        metadata = source.metadata
        label_map = dict()
        # append existing data using XPath expressions (for parsing)
        for i in self._FIELD_LABEL:
            if i in metadata['info'] and (not (i in self._ADDR_FIELD_LABEL)) and i != 'address':
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
        Parses a dataset in XML format using the xml.etree.ElementTree module and 
        extracts the necessary information to rewrite the data set into CSV format, 
        as specified by a source file.

        Args:
            json_data: dictionary obtained by json.load when read from a source file

        Raises:
            ElementTree.ParseError: Incorrect XML format of the specified dataset.

        Returns:
            Return values are interpreted by 'process.py' as follows:
            '0' : Successful reformatting.
            '1' : Incorrect formatting of XML dataset.
        """
        if not hasattr(source, 'label_map'):
            raise ValueError("Source object missing 'label_map', 'extract_labels' was not ran.")

        filename = source.metadata['file']
        tags = source.label_map
        header = source.metadata['header']
        enc = self.char_encode_check(source)
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse('./pddir/raw/' + filename, parser=xmlp)
        root = tree.getroot()

        if len(filename.split('.')) == 1:
            source.dirtypath = filename + "-DIRTY.csv"
        else:
            source.dirtypath = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"

        csvfile = open(source.dirtypath, 'w')
        cprint = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # write the initial row which identifies each column
        first_row = [f for f in tags]
        if "full_addr" in first_row:
            ind = first_row.index("full_addr")
            first_row.pop(ind)
            for af in reversed(self._ADDR_FIELD_LABEL):
                first_row.insert(ind, af)
        cprint.writerow(first_row)

        for element in root.iter(header):
            row = []
            for key in tags:
                if isinstance(tags[key], list) and key not in self._FORCE_LABEL:
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
                        for af in self._ADDR_FIELD_LABEL:
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
                    for af in self._ADDR_FIELD_LABEL:
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


    def clean(self):
        pass

    def _xml_empty_element_handler(self, element):
        """
        The 'xml.etree' module returns 'None' for text of empty-element tags. Moreover, 
        if the element cannot be found, the element is 'None'. This function is defined 
        to handle these cases.

        Note:
            This function is used by 'xml_parse'.

        Args:
            element: A node in the XML tree.

        Returns:
            'True' is returned if element's tag is missing from the header. From here,
            'xml_parse' returns a detailed error message of the missing tag and 
            terminates the data processing.

            Otherwise, return the appropriate field contents.
        """
        if element is None: # if the element is missing, return error
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
    Source dataset class.
    """
    def __init__(self, path):
        """
        New source file object is created.
        """
        if not os.path.exists(path):
            raise OSError('Path "%s" does not exist.' % path)
        self.srcpath = path
        self.rawpath = None
        self.dirtypath = None
        self.cleanpath = None
        self.label_map = None
        with open(path) as f:
            self.metadata = json.load(f)

    def parse(self):
        """
        Parses the source file. 
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
            raise ValueError("'header' must be a string.")

        # url
        if 'url' in self.metadata and (not isinstance(self.metadata['url'], str)):
            raise ValueError("'url' must be a string.")


        # check that both full_addr and address are not in the source file
        if ('address' in self.metadata['info']) and ('full_addr' in self.metadata['info']):
            raise ValueError("Cannot have both 'full_addr' and 'address' tags in source file.")

        # verify address is an object with valid tags
        if 'address' in self.metadata['info']:
            if not (isinstance(self.metadata['info']['address'], dict)):
                raise TypeError("'address' tag must be an object.")

            for i in self.metadata['info']['address']:
                if not (i in data_parser.ADDR_FIELD_LABEL): # DEBUG ##################### 
                    raise ValueError("'address' tag contains an invalid key.")

        # verify force is an object with valid tags
        if 'force' in self.metadata:
            if not (isinstance(self.metadata['force'], dict)):
                raise TypeError("'force' tag must be an object.")

            for i in self.metadata['force']:
                if not (i in data_parser.FORCE_LABEL): # DEBUG ##################### 
                    raise ValueError("'force' tag contains an invalid key.")
                elif ('address' in self.metadata['info']) and (i in self.metadata['info']['address']):
                    raise ValueError("Key '", i, "' appears in 'force' and 'address'.")

    def fetch_url(self):
        """
        Fetches URL.
        """
        response = urllib.request.urlopen(self.metadata['url'])
        bytedata = response.read()
        with open('./pddir/raw/' + self.metadata['file'], 'wb') as data_file:
            data_file.write(bytedata)

    def raw_data_exists(self):
        """
        Checks if raw dataset exists.
        """
        if not path.exists('./pddir/raw/' + self.metadata['file']):
            raise OSError("'" + self.metadata['file'] + "' not found in raw folder.")


######################
# OBR.PY DEBUG BLOCK #
######################

if __name__ == "__main__":
    from postal.parser import parse_address
    s = Source('./sources/misc/msbregistry.json')
    d = DataProcess(s, parse_address)
    d.process()
    
