"""
This module defines the OpenTabulate API, which contains classes and methods 
for a data processing production system. In abstraction, Source objects are 
created to represent everything about a dataset, such as its metadata and 
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

#
# Comments prefixes:
# 
# IMPORTANT - self explanatory
# SUGGESTION - self explanatory
# DEBUG - inserted code for the purpose of testing
#

###########
# MODULES #
###########

import csv
import json
import operator
import os
import re
import requests
import subprocess
import sys
import urllib.request as req

from xml.etree import ElementTree
from zipfile import ZipFile


#############################
# CORE DATA PROCESS CLASSES #
#############################

class DataProcess(object):
    """
    A data processing interface for a source file. If no arguments for the
    __init__ method are provided, they default to 'None'.

    Attributes:

      source: A dataset and its associated metadata, defined as a Source 
        object.

      dp_address_parser: An object containing an address parser method,
        defined by an AddressParser object.
    """
    def __init__(self, source=None, address_parser=None, algorithm=None):
        """
        Initialize a DataProcess object.

        Args:
        
          source: A dataset and its associated metadata, defined
            as a Source object.

          address_parser: An address parsing function which accepts a
            string as an argument.

          algorithm: An object that is a child class of Algorithm.
        """
        self.source = source

        if address_parser != None:
            self.dp_address_parser = AddressParser(address_parser)

        self.algorithm = algorithm

    def setAddressParser(self, address_parser):
        """
        Set the current address parser.
        """
        self.dp_address_parser = AddressParser(address_parser)

    def preprocessData(self):
        """
        (EXPERIMENTAL) Execute external scripts before processing. 

        This is a "dangerous" method, in that it permits arbitrary execution
        of a script which is sent a single command line argument, which is
        self.source.rawpath. The file name MUST NOT be altered! The script
        must adjust the file inline or create a temporary copy that will
        overwrite the original. 
        """

        # check if a preprocessing script is provided
        if 'pre' in self.source.metadata:
            scr = self.source.metadata['pre']
        else:
            return None

        # string argument for script path
        if isinstance(scr, str):
            print('[DEBUG]: Running preprocessing script "%s".' % scr)
            rc = subprocess.call([scr, self.source.rawpath])
            print('[DEBUG]: process return code %d.' % rc)
        # list of strings argument for script path
        elif isinstance(scr, list):
            for subscr in scr:
                print('[DEBUG]: Running preprocessing script "%s".' % subscr)
                rc = subprocess.call([subscr, self.source.rawpath])
                print('[DEBUG]: process return code %d.' % rc)

                
    def prepareData(self):
        """
        'Algorithm' wrapper method. Selects a child class of 'Algorithm' to prepare formatting
        of data into a standardized CSV format.
        """
        if self.source.metadata['format'] == 'csv':
            fmt_algorithm = CSV_Algorithm(self.dp_address_parser, self.source.metadata['database_type'])
            fmt_algorithm.format_correction(self.source, fmt_algorithm.char_encode_check(self.source))
        elif self.source.metadata['format'] == 'xml':
            fmt_algorithm = XML_Algorithm(self.dp_address_parser, self.source.metadata['database_type'])
        # need the following line so the Algorithm wrapper methods work
        self.algorithm = fmt_algorithm
        
    def extractLabels(self):
        """
        'Algorithm' wrapper method. Extracts data labels as indicated by a source file.
        """
        self.algorithm.extract_labels(self.source)

    def parse(self):
        """
        'Algorithm' wrapper method. Parses the source dataset based on label extraction,
        and reformats the data into a dirty CSV file.
        """
        self.algorithm.parse(self.source)

    def clean(self):
        """
        'Algorithm' wrapper method. Applies basic data cleaning to a recently parsed
        and reformatted dataset.
        """
        self.algorithm.clean(self.source)

    def postprocessData(self):
        """
        (EXPERIMENTAL) Execute external scripts after processing and cleaning.

        This is a "dangerous" method, in that it permits arbitrary execution
        of a script which is sent a single command line argument, which is
        self.source.cleanpath. The file name MUST NOT be altered! The script
        must adjust the file inline or create a temporary copy that will
        overwrite the original. 
        """

        # check if a preprocessing script is provided
        if 'post' in self.source.metadata:
            scr = self.source.metadata['post']
        else:
            return None

        # string argument for script path
        if isinstance(scr, str):
            print('[DEBUG]: Running postprocess script "%s".' % scr)
            rc = subprocess.call([scr, self.source.cleanpath])
            print('[DEBUG]: process return code %d.' % rc)
        # list of strings argument for script path
        elif isinstance(scr, list):
            for subscr in scr:
                print('[DEBUG]: Running postprocess script "%s".' % subscr)
                rc = subprocess.call([subscr, self.source.cleanpath])
                print('[DEBUG]: process return code %d.' % rc)


    def blankFill(self):
        """
        'Algorithm' wrapper method. Adds columns from the standard list by appending 
        blanks.
        """
        self.algorithm.blank_fill(self.source)

class AddressParser(object):
    """
    Wrapper class for an address parser.

    Currently supported parsers: libpostal

    Attributes:

      address_parser: Address parsing function.
    """
    def __init__(self, address_parser=None):
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

        Returns:

          self.address_parser(addr): parsed address in libpostal 
            format.
        """
        return self.address_parser(addr)


#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm(object):
    """
    Parent algorithm class for data processing.

    Attributes:

      FIELD_LABEL: Standardized field names for the database type.

      ADDR_FIELD_LABEL: Standardized address field names.

      ENCODING_LIST: List of character encodings to test.

      address_parser: Address parsing function to use.
    """

    # general data labels (e.g. contact info, location)
    _GENERAL_LABELS = ['full_addr', 'street_no', 'street_name', 'postcode', 'unit', 'city', 'prov/terr', 'country', \
                       'comdist', 'region', \
                       'longitude', 'latitude', \
                       'phone', 'fax', 'email', 'website', 'tollfree']

    # business data labels
    _BUSINESS_LABELS = ['bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc', \
                        'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active', \
                        'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',\
                        'home_bus', 'munic_bus', 'nonres_bus', \
                        'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3', \
                        'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6', \
                        'naics_desc', \
                        'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2', \
                        'facebook', 'twitter', 'linkedin', 'youtube', 'instagram']

    # education data labels
    _EDU_FACILITY_LABELS = ['ins_name', 'ins_type', 'ins_code', 'edu_level', 'board_name', \
                            'board_code', 'school_yr', 'range', 'kindergarten', 'elementary', \
                            'secondary', 'post-secondary']

    # supported address field labels
    # note that the labels are ordered to conform to the Canada Post mailing address standard
    ADDR_FIELD_LABEL = ['unit', 'street_no', 'street_name', 'city', 'prov/terr', 'country', 'postcode']

    # supported encodings (as defined in Python standard library)
    ENCODING_LIST = ["utf-8", "cp1252", "cp437"]
    
    # conversion table for address labels to libpostal tags
    _ADDR_LABEL_TO_POSTAL = {'street_no' : 'house_number', \
                            'street_name' : 'road', \
                            'unit' : 'unit', \
                            'city' : 'city', \
                            'prov/terr' : 'state', \
                            'country' : 'country', \
                            'postcode' : 'postcode' }


    def __init__(self, address_parser=None, database_type=None):
        """
        Initializes Algorithm object.

        Args:
          address_parser: AddressParser object. This is designed for an
            AddressParser object or 'None'.
        """
        self.address_parser = address_parser
        self.database_type = database_type
        
        if self.database_type == "education":
            self.FIELD_LABEL = self._EDU_FACILITY_LABELS + self._GENERAL_LABELS
        else: # default to business
            self.FIELD_LABEL = self._BUSINESS_LABELS + self._GENERAL_LABELS
    

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
            data_enc = metadata['encoding']
            if data_enc in self.ENCODING_LIST:
                return data_enc
            else:
                raise ValueError(data_enc + " is not a valid encoding.")
        else:
            for enc in self.ENCODING_LIST:
                try:
                    with open('./pddir/raw/' + source.local_fname, encoding=enc) as f:
                        for line in f:
                            pass
                    return enc
                except UnicodeDecodeError:
                    pass
            raise RuntimeError("Could not guess original character encoding.")


    ############################################
    # Support functions for the 'parse' method #
    ############################################

    def _generateFirstRow(self, tags):
        row = [t for t in tags]
        if "full_addr" in row:
            ind = row.index("full_addr")
            row.pop(ind)
            for atag in reversed(self.ADDR_FIELD_LABEL):
                row.insert(ind, atag)
        return row

    def _isRowEmpty(self, row):
        """
        Checks if a list 'row' consists of only empty string entries.
        """
        for element in row:
            if element != "":
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
        # 'f' refers to the original file, 'bff' refers to the new blank filled file
        with open(source.cleanpath, 'r') as f, open(source.cleanpath + '.bf', 'w') as bff:
            # initialize csv reader/writer
            rf = csv.DictReader(f)
            wf = csv.writer(bff, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            wf.writerow(LABELS)

            for old_row in rf:
                row2write = []
                for col in LABELS:
                    if col not in old_row:
                        row2write.append("")
                    else:
                        row2write.append(old_row[col])
                wf.writerow(row2write)
                

    def clean(self, source):
        """
        A general dataset cleaning method.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.
        """
        error_flag = False
        
        with open(source.dirtypath, 'r') as dirty, \
             open(source.cleanpath, 'w') as clean, \
             open(source.cleanpath + ".errors", 'w') as error:

            csvreader = csv.DictReader(dirty)
            csvwriter = csv.DictWriter(clean, fieldnames=csvreader.fieldnames, quoting=csv.QUOTE_ALL)

            error_headers = ['ERROR'] + csvreader.fieldnames
            csverror = csv.DictWriter(error, fieldnames=error_headers, quoting=csv.QUOTE_ALL)
            
            csvwriter.writeheader()
            csverror.writeheader()
            
            for row in csvreader:
                # general field cleaning
                # clean postal codes
                if 'postcode' in csvreader.fieldnames and row['postcode'] != '':
                    postal_code = row['postcode']
                    postal_code = re.sub(r"\s+", "", postal_code)
                    postal_code = postal_code.upper()
                    row['postcode'] = postal_code

                    # check string length
                    if len(postal_code) != 6:
                        row['ERROR'] = "postcode:"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                    # check character frequency
                    alpha = 0
                    digit = 0
                    for c in postal_code:
                        if c.isalpha():
                            alpha += 1
                        elif c.isdigit():
                            digit += 1
                    if alpha != 3 or digit != 3:
                        row['ERROR'] = "postcode:"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                    # check structure
                    if not re.match(r'[A-Z][0-9][A-Z][0-9][A-Z][0-9]', postal_code):
                        row['ERROR'] = "postcode"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                if 'phone' in csvreader.fieldnames and row['phone'] != '':
                    phone_number = row['phone']
                    phone_number = re.sub(r"[\s\(\)-]", "", phone_number)
                    row['phone'] = phone_number

                if 'fax' in csvreader.fieldnames and row['fax'] != '':
                    fax_number = row['fax']
                    fax_number = re.sub(r"[\s\(\)-]", "", fax_number)
                    row['fax'] = fax_number

                
                if 'prov/terr' in csvreader.fieldnames and row['prov/terr'] != '':
                    province_territory_shortlist = ["ab", "bc", "mb", "nb", "nl", "ns", "nt", "nu", "on", "pe", "qc", "sk", "yt"]
                    long_to_short_map = {"alberta": "ab", \
                                         "british columbia": "bc", \
                                         "manitoba": "mb", \
                                         "new brunswick": "nb", \
                                         "newfoundland": "nl", \
                                         "nova scotia": "ns", \
                                         "northwest territories": "nt", \
                                         "nunavut": "nu", \
                                         "ontario": "on", \
                                         "prince edward island": "pe", \
                                         "québec": "qc", \
                                         "saskatchewan": "sk", \
                                         "yukon": "yt"}

                    if row['prov/terr'] in province_territory_shortlist:
                        pass
                    elif row['prov/terr'] in long_to_short_map:
                        row['prov/terr'] = long_to_short_map[row['prov/terr']]
                    else:
                        row['ERROR'] = "prov/terr"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                if 'country' in csvreader.fieldnames and row['country'] != '':
                    if row['country'] in ["ca", "canada"]:
                        row['country'] = "ca"
                    else:
                        row['ERROR'] = "country"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                # business label cleaning
                if self.database_type == "business":
                    pass
                    
                # education label cleaning
                if self.database_type == "education":
                    pass

                
                csvwriter.writerow(row)
                    
        if error_flag == False:
            os.remove(source.cleanpath + ".errors")
        os.remove(source.dirtypath)
    
class CSV_Algorithm(Algorithm):
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
            # short circuit evaluation
            elif ('address' in metadata['info']) and (i in metadata['info']['address']):
                label_map[i] = metadata['info']['address'][i] 
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

        tags = source.label_map
        enc = self.char_encode_check(source)

        with open(source.dirtypath, 'r', encoding=enc) as csv_file_read, \
             open(source.dirtypath + '-temp', 'w', encoding="utf-8") as csv_file_write:
            csvreader = csv.DictReader(csv_file_read)
            csvwriter = csv.writer(csv_file_write, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # write the initial row which identifies each column
            col_labels = self._generateFirstRow(tags)
            csvwriter.writerow(col_labels)

            try:
                for entity in csvreader:
                    row = []
                    for key in tags:
                        # # #
                        # decision: Check if tags[key] is of type JSON array (list).
                        #
                        # depth: 1
                        # # #
                        if isinstance(tags[key], list):
                            entry = ''
                            for i in tags[key]:
                                # check if 'i' is of the form 'force:*'
                                ii = i.split(':')
                                if len(ii) == 1:
                                    entry += entity[i] + ' '
                                elif len(ii) == 2:
                                    entry += ii[1] + ' '
                            entry = self._quick_scrub(entry)
                            # # #
                            # decision: check if key is "full_addr"
                            # depth: 2
                            # # #
                            if key != "full_addr":
                                row.append(entry)
                            else:
                                ap_entry = self.address_parser.parse(entry)
                                # SUGGESTION: This for loop is exclusively for libpostal output.
                                # Perhaps it should be moved to the AddressParser object?
                                for afl in self.ADDR_FIELD_LABEL:
                                    if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                        ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                        row.append(ap_entry[ind][0])
                                    else:
                                        row.append("")
                            continue
                        # # #
                        # decision: check if key is "full_addr"
                        # depth: 1
                        # # #
                        if key == "full_addr":
                            entry = entity[tags[key]]
                            entry = self._quick_scrub(entry)
                            ap_entry = self.address_parser.parse(entry)
                            # SUGGESTION: This for loop is exclusively for libpostal output.
                            # Perhaps it should be moved to the AddressParser object?
                            for afl in self.ADDR_FIELD_LABEL:
                                if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                    ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                    row.append(ap_entry[ind][0])
                                else:
                                    row.append("")
                            continue
                        # # #
                        # All other cases get handled here.
                        # # #
                        # check if 'tags[key]' is of the form 'force:*'
                        ee = tags[key].split(':')
                        if len(ee) == 1:
                            entry = self._quick_scrub(entity[ee[0]])
                        elif len(ee) == 2:
                            entry = self._quick_scrub(ee[1])
                        row.append(entry)
                    if not self._isRowEmpty(row):
                        csvwriter.writerow(row)
            except KeyError:
                print("[ERROR] ", source.local_fname," :'", tags[key], "' is not a field name in the CSV file. ", file=sys.stderr, sep='')
                # DEBUG: need a safe way to exit from here!!!
                exit(1)

        os.rename(source.dirtypath + '-temp', source.dirtypath)

        
    def format_correction(self, source, data_encoding):
        """
        Deletes rows of CSV datasets that have a number of entries not
        agreeing with the total number of columns. Additionally removes a
        byte order mark if it exists.

        Args:

          source: A dataset and its associated metadata, defined as a Source 
            object.

          data_encoding: The character encoding of the data.
        """
        error_flag = False
        
        with open(source.rawpath, 'r', encoding=data_encoding) as raw, \
             open(source.dirtypath, 'w', encoding=data_encoding) as dirty, \
             open(source.dirtypath + '.errors', 'w', encoding=data_encoding) as error:
            reader = csv.reader(raw)
            writer = csv.writer(dirty)
            errors = csv.writer(error)
            
            flag = False
            size = 0
            first_row = True
            line = 1
            
            for row in reader:
                if first_row == True:
                    row[0] = re.sub(r"^\ufeff(.+)", r"\1", row[0])
                    first_row = False

                if flag == True:
                    if len(row) != size:
                        error_flag = True
                        print("ERROR: Missing or too many entries on line ", line, ".", sep='')
                        errors.writerow(["FC" + str(line)] + row) # FC for format correction method
                        line += 1
                        continue
                    else:
                        writer.writerow(row)
                else:
                    size = len(row)
                    flag = True
                    writer.writerow(row)
                    errors.writerow(['ERROR'] + row)
                line += 1

        if error_flag == False:
            os.remove(source.dirtypath + '.errors')

class XML_Algorithm(Algorithm):
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
                # note that the labels have to map to XPath expressions
                label_map[i] = ".//" + metadata['info']['address'][i]
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

        tags = source.label_map
        header = source.metadata['header']
        enc = self.char_encode_check(source)
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(source.rawpath, parser=xmlp)
        root = tree.getroot()

        with open(source.dirtypath, 'w', encoding="utf-8") as csvfile:
            
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # write the initial row which identifies each column
            col_labels = self._generateFirstRow(tags)
            csvwriter.writerow(col_labels)

            for element in root.iter(header):
                row = []
                for key in tags:
                    # # #
                    # decision: Check if tags[key] is of type JSON array (list).
                    # By design, FORCE keys should be ignored in this decision.
                    #
                    # depth: 1
                    # # #
                    if isinstance(tags[key], list):
                        entry = ''
                        for i in tags[key]:
                            # check if 'i' is of the form 'force:*'
                            ii = i.split(':')
                            if len(ii) == 1:
                                subelement = element.find(i)
                                subelement = self._xml_empty_element_handler(subelement)
                                entry += subelement + ' '
                            elif len(ii) == 2:
                                entry += ii[1] + ' '
                        entry = self._quick_scrub(entry)
                        # # #
                        # decision: check if key is "full_addr"
                        # depth: 2
                        # # #
                        if key != "full_addr":
                            row.append(entry)
                        else:
                            ap_entry = self.address_parser.parse(entry)
                            # SUGGESTION: This for loop is exclusively for libpostal output.
                            # Perhaps it should be moved to the AddressParser object?
                            for afl in self.ADDR_FIELD_LABEL:
                                if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                    ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                    row.append(ap_entry[ind][0])
                                else:
                                    row.append("")
                        continue
                    # # #
                    # decision: check if key is "full_addr"
                    # depth: 1
                    # # #
                    if key == "full_addr":
                        entry = element.find(tags[key])
                        entry = self._xml_empty_element_handler(entry)
                        entry = self._quick_scrub(entry)
                        ap_entry = self.address_parser.parse(entry)
                        # SUGGESTION: This for loop is exclusively for libpostal output.
                        # Perhaps it should be moved to the AddressParser object?
                        for afl in self.ADDR_FIELD_LABEL:
                            if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                row.append(ap_entry[ind][0])
                            else:
                                row.append("")
                        continue
                    # # #
                    # All other cases get handled here.
                    # # #
                    # check if 'tags[key]' is of the form 'force:*'
                    ee = tags[key].split(':')
                    if len(ee) == 1:
                        subelement = element.find(ee[0])
                        subel_content = self._xml_empty_element_handler(subelement)
                    elif len(ee) == 2:
                        subel_content = ee[1]
                    row.append(self._quick_scrub(subel_content))
                if not self._isRowEmpty(row):
                    csvwriter.writerow(row)




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

      metadata: JSON dumps from source file

      local_fname: 'root' name of the dataset file (without prefixes)

      rawpath: path to the raw dataset relative to the OBR directory. This is
        assigned './pddir/raw'.

      dirtypath: path to the dirty dataset relative to the OBR directory. This is
        assigned './pddir/dirty'.

      cleanpath: path to the clean dataset relative to the OBR directory. This is
        assigned './pddir/clean'.

      label_map: a dict object that stores the mapping of OBRs standardized labels
        to the dataset's labels, as obtained by the source file.

      database_type: string which indicates the type of database, intended to be
        interpreted by the DataProcess class when determining standardized column 
        names.
    """
    def __init__(self, path, pre_flag=False, post_flag=False, no_fetch_flag=True, \
                 no_extract_flag=True, blank_fill_flag=False):
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

        # determined by command line arguments
        self.pre_flag = pre_flag
        self.post_flag = post_flag
        self.no_fetch_flag = no_fetch_flag
        self.no_extract_flag = no_extract_flag
        self.blank_fill_flag = blank_fill_flag
        
        # determined during parsing
        self.local_fname = None
        self.rawpath = None
        self.dirtypath = None
        self.cleanpath = None
        self.label_map = None
        self.database_type = None

    def parse(self):
        """
        Parses the source file to check correction of syntax.

        Raises:

          LookupError: Associated with a missing tag.

          ValueError: Associated with an incorrect entry or combination or entries.
            For example, having an 'address' and 'full_addr' tag will raise this
            error since they cannot both be used in a source file.

          TypeError: Associated with an incorrect JSON type for a tag.

          OSError: A path for pre or post processing scripts was not found.
        """
        # required tags
        if 'format' not in self.metadata:
            raise LookupError("'format' tag is missing.")
        if 'localfile' not in self.metadata:
            raise LookupError("'localfile' tag is missing.")
        if 'info' not in self.metadata:
            raise LookupError("'info' tag is missing.")
        if 'database_type' not in self.metadata:
            raise LookupError("'database_type' tag is missing.")

        # required tag types
        if not isinstance(self.metadata['format'], str):
            raise TypeError("'format' must be a string.")
        if not isinstance(self.metadata['localfile'], str):
            raise TypeError("'localfile' must be a string.")
        if not isinstance(self.metadata['info'], dict):
            raise TypeError("'info' must be an object.")
        if not isinstance(self.metadata['database_type'], str):
            raise TypeError("'database_type' must be a string.")

        # required formats
        if (self.metadata['format'] != 'xml') and (self.metadata['format'] != 'csv'):
            raise ValueError("Unsupported data format '" + self.metadata['format'] + "'")

        # required database types
        if (self.metadata['database_type'] != 'business') and \
           (self.metadata['database_type'] != 'education'):
            raise ValueError("Unsupported database type '" + self.metadata['database_type'] + "'")

        # OPTIONAL TAGS
        
        # required header if format is not csv
        if (self.metadata['format'] != 'csv') and ('header' not in self.metadata):
            raise LookupError("'header' tag missing for format " + self.metadata['format'])

        if (self.metadata['format'] != 'csv') and ('header' in self.metadata) and (not isinstance(self.metadata['header'], str)):
            raise TypeError("'header' must be a string.")

        # url
        if 'url' in self.metadata and (not isinstance(self.metadata['url'], str)):
            raise TypeError("'url' must be a string.")

        # compression
        if 'compression' in self.metadata:
            if not isinstance(self.metadata['compression'], str):
                raise TypeError("'compression' must be a string.")
            if self.metadata['compression'] != 'zip':
                raise ValueError("Unsupported compression format '" + self.metadata['compression'] + "'")

        # localarchive
        if ('localarchive' in self.metadata) and ('compression' not in self.metadata):
            raise LookupError("'compression' tag missing for localarchive " + self.metadata['localarchive'])

        # preprocessing type and path existence check
        if 'pre' in self.metadata:
            if not (isinstance(self.metadata['pre'], str) or isinstance(self.metadata['pre'], list)):
                raise TypeError("'pre' must be a string or a list of strings.")

            if isinstance(self.metadata['pre'], list):
                for entry in self.metadata['pre']:
                    if not isinstance(entry, str):
                        raise TypeError("'pre' must be a string or a list of strings.")

            if isinstance(self.metadata['pre'], str) and not os.path.exists(self.metadata['pre']):
                raise OSError('Preprocessing script "%s" does not exist.' % script_path)
            elif isinstance(self.metadata['pre'], list):
                for script_path in self.metadata['pre']:
                    if not os.path.exists(script_path):
                        raise OSError('Preprocessing script "%s" does not exist.' % script_path)

        # postprocessing type and path existence check
        if 'post' in self.metadata:
            if not (isinstance(self.metadata['post'], str) or isinstance(self.metadata['post'], list)):
                raise TypeError("'post' must be a string or a list of strings.")

            if isinstance(self.metadata['post'], list):
                for entry in self.metadata['post']:
                    if not isinstance(entry, str):
                        raise TypeError("'post' must be a string or a list of strings.")

            if isinstance(self.metadata['post'], str) and not os.path.exists(self.metadata['post']):
                raise OSError('Postprocessing script "%s" does not exist.' % script_path)
            elif isinstance(self.metadata['post'], list):
                for script_path in self.metadata['post']:
                    if not os.path.exists(script_path):
                        raise OSError('Postprocessing script "%s" does not exist.' % script_path)                    


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

        
        # set local_fname, rawpath, dirtypath, and cleanpath values
        self.local_fname = self.metadata['localfile'].split(':')[0]
        self.rawpath = './pddir/raw/' + self.local_fname
        if len(self.local_fname.split('.')) == 1:
            self.dirtypath = './pddir/dirty/' + self.local_fname + "-dirty.csv"
        else:
            self.dirtypath = './pddir/dirty/' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + "-dirty.csv"

        if len(self.local_fname.split('.')) == 1:
            self.cleanpath = './pddir/clean/' + self.local_fname + "-clean.csv"
        else:
            self.cleanpath = './pddir/clean/' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + "-clean.csv"

                
    def fetch_url(self):
        """
        Downloads a dataset by fetching its URL and writing to the raw directory.
        """
        if self.no_fetch_flag == True:
            return None
        
        # use requests library if protocol is HTTP
        if self.metadata['url'][0:4] == "http":
            response = requests.get(self.metadata['url'])
            content = response.content
        # otherwise, use urllib to handle other protocols (e.g. FTP)
        else:
            response = req.urlopen(self.metadata['url'])
            content = response.read()
            
        if 'compression' in self.metadata:
            if self.metadata['compression'] == "zip":
                with open('./pddir/raw/' + self.metadata['localarchive'], 'wb') as data:
                    data.write(content)
        else:
            with open('./pddir/raw/' + self.metadata['localfile'], 'wb') as data:
                data.write(content)

    def archive_extraction(self):
        if self.no_extract_flag == True:
            return None
        
        if self.metadata['compression'] == "zip":
            with ZipFile('./pddir/raw/' + self.metadata['localarchive'], 'r') as zip_file:
                archive_fname = self.metadata['localfile'].split(':')
                if len(archive_fname) == 1:
                    zip_file.extract(archive_fname[0], './pddir/raw/')
                else:
                    zip_file.extract(archive_fname[1], './pddir/raw/')
                    os.rename('./pddir/raw/' + archive_fname[1], './pddir/raw/' + self.local_fname)

############################
# LOGGING / DEBUGGING MODE #
############################

class Logger(object):
    """
    (IN PROGRESS) A logging class to write logs for debugging.
    """
    def __init__(self, id, logfile="pdlog.txt"):
        self.log = open(id + ".tmp", 'w')
        self.logfile = logfile
        self.id = id

    def write(self, message):
        self.log.write(message)

    def flush(self):
        self.log.flush()

    def __enter__(self):
        return self

    def __exit__(self):
        self.log.close()

class Logger(object):
    """
    (IN PROGRESS) A logging class to write logs for debugging.
    """
    def __init__(self, id, logfile="pdlog.txt"):
        self.log = open(id + ".tmp", 'w')
        self.logfile = logfile
        self.id = id

    def write(self, message):
        self.log.write(message)

    def flush(self):
        self.log.flush()

    def __enter__(self):
        return self

    def __exit__(self):
        self.log.close()
