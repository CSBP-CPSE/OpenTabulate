# -*- coding: utf-8 -*-
"""
Tabulation and processing API.

This module defines the core OpenTabulate API, which contains classes and methods 
for parsing, processing, and reformatting microdata into CSV format. Source objects 
are abstractions of datasets, which reads and stores important metadata upon use of 
the Source constructor. The dynamic modification of Source objects by DataProcess 
objects abstracts the data processing. A DataProcess object uses the Algorithm 
class methods and its child classes to process specific data formats, such as
CSV and XML format.


Created and written by Maksym Neyra-Nesterenko.

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""

# - Additional notes -
#
# Code comment prefixes: 
# IMPORTANT, SUGGESTION, DEBUG
# ---

###########
# MODULES #
###########

import csv
import json
import logging
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
    A data processing interface for a source file. 

    If no arguments for the __init__ method are provided, arguments are set to None.
    
    Attributes:
        source (Source): Dataset abstraction.
        dp_address_parser (AddressParser): Address parser wrapper.
    """
    def __init__(self, source=None, address_parser=None, algorithm=None):
        """
        Initialize a DataProcess object.

        Args:
            source (Source): Dataset abstraction.
            address_parser (function): Address parsing function, accepts a 
                string as an argument.
            algorithm (obj(Algorithm)): Any child class of Algorithm.
        """
        self.source = source

        if address_parser != None:
            self.dp_address_parser = AddressParser(address_parser)
        else:
            self.dp_address_parser = None

        self.algorithm = algorithm

    def setAddressParser(self, address_parser):
        '''Set the current address parser.'''
        self.dp_address_parser = AddressParser(address_parser)

    def preprocessData(self):
        """
        Execute external scripts before processing.

        To use your script, it must be written to accept TWO command line arguments, 
        one which is a path to the file to preprocess and the other being a path of 
        the output. The paths MUST NOT be altered!
        """
        # check if a preprocessing script is provided
        if 'pre' in self.source.metadata:
            scr = self.source.metadata['pre']
        else:
            return None

        # string argument for script path
        if isinstance(scr, str):
            rc = subprocess.call([scr, self.source.rawpath, self.source.prepath])
            self.source.log.warning("'%s' return code: %d" % (scr, rc))
        # list of strings argument for script path
        elif isinstance(scr, list):
            num = len(scr)
            for i in range(num):
                if i != 0:
                    rc = subprocess.call([scr[i], self.source.prepath, self.source.prepath_temp])
                    self.source.log.warning("'%s' return code: %d" % (scr[i], rc))
                    os.rename(self.source.prepath_temp, self.source.prepath)
                else:
                    rc = subprocess.call([scr[i], self.source.rawpath, self.source.prepath])
                    self.source.log.warning("'%s' return code: %d" % (scr[i], rc))

                
    def prepareData(self):
        """
        Algorithm wrapper method. 

        Selects a child class of 'Algorithm' to prepare formatting of data into a 
        standardized CSV format.
        """
        if self.source.metadata['format'] == 'csv':
            fmt_algorithm = CSV_Algorithm(self.dp_address_parser, self.source.metadata['database_type'])
            csv_encoding = fmt_algorithm.char_encode_check(self.source)
            self.source.metadata['encoding'] = csv_encoding # to prevent redundant brute force encoding checks
            fmt_algorithm.csv_format_correction(self.source, csv_encoding)
        elif self.source.metadata['format'] == 'xml':
            fmt_algorithm = XML_Algorithm(self.dp_address_parser, self.source.metadata['database_type'])
            #fmt_algorithm.remove_xmlns(self.source)
        # need the following line so the Algorithm wrapper methods work
        self.algorithm = fmt_algorithm
        
    def extractLabels(self):
        """
        Algorithm wrapper method. 

        Extracts data labels as indicated by a source file.
        """
        self.algorithm.extract_labels(self.source)

    def parse(self):
        """
        Algorithm wrapper method. 

        Parses and tabulates the source dataset based on label extraction.
        """
        self.algorithm.parse(self.source)

    def clean(self):
        """
        Algorithm wrapper method. 

        Applies basic data cleaning to a tabulated dataset.
        """
        self.algorithm.clean(self.source)

    def postprocessData(self):
        """
        Execute external scripts after processing and cleaning.

        The scripts are defined so that they accept a single command line argument, 
        which is a path to the data to postprocess. The path MUST NOT be altered!
        """
        # check if a preprocessing script is provided
        if 'post' in self.source.metadata:
            scr = self.source.metadata['post']
        else:
            return None

        # string argument for script path
        if isinstance(scr, str):
            rc = subprocess.call([scr, self.source.cleanpath])
            self.source.log.warning("'%s' return code: %d" % (scr, rc))
        # list of strings argument for script path
        elif isinstance(scr, list):
            for subscr in scr:
                rc = subprocess.call([subscr, self.source.cleanpath])
                self.source.log.warning("'%s' return code: %d" % (subscr, rc))


class AddressParser(object):
    """
    Wrapper class for an address parser.

    Currently supported parsers: 
        * libpostal

    Attributes:
        address_parser (function): Address parsing function, accepts a string 
            as an argument.
    """
    def __init__(self, address_parser=None):
        """
        Initialize an AddressParser object.

        Args:
            address_parser (function): Address parsing function, accepts a string 
                as an argument.
        """
        self.address_parser = address_parser

    def parse(self, addr):
        """
        Parses an address string and returns the tokens.

        Args:
            addr (str): A string containing the address to parse.

        Returns:
            self.address_parser(addr) (?): Parsed address in libpostal format.
        """
        return self.address_parser(addr)


#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm(object):
    """
    Parent algorithm class for data processing.

    Attributes:
        FIELD_LABEL (tuple): Standardized field names for the database type.
        ADDR_FIELD_LABEL (tuple): Standardized address field names.
        ENCODING_LIST (tuple): List of character encodings to test.
        address_parser (function): Address parsing function, accepts a 
            string as an argument.
    """

    # general data labels (e.g. contact info, location)
    _GENERAL_LABELS = ('address_str', 'street_no', 'street_name', 'postal_code', 'unit', 'city', 'region', 'country',
                       'longitude', 'latitude',
                       'phone', 'fax', 'email', 'website', 'tollfree')

    # business data labels
    _BUSINESS_LABELS = ('legal_name', 'trade_name', 'business_type', 'business_no', 'bus_desc',
                        'licence_type', 'licence_no', 'start_date', 'closure_date', 'active',
                        'no_emp', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                        'home_bus', 'munic_bus', 'nonres_bus',
                        'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                        'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                        'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2')

    # education data labels
    _EDU_FACILITY_LABELS = ('institution_name', 'institution_type', 'ins_code', 'education_level', 'board_name',
                            'board_code', 'school_yr', 'range', 'isced010', 'isced020', 'isced1',
                            'isced2', 'isced3', 'isced4+')

    # hospital data labels
    _HOSPITAL_LABELS = ('hospital_name','hospital_type','health_authority')

    # hospital data labels
    _LIBRARY_LABELS = ('library_name','library_type','library_board')

    # fire station labels
    _FIRE_STATION_LABELS = ('fire_station_name',)

    # supported address field labels
    # note that the labels are ordered to conform to the Canada Post mailing address standard
    ADDR_FIELD_LABEL = ('unit', 'street_no', 'street_name', 'city', 'region', 'country', 'postal_code')

    # supported encodings (as defined in Python standard library)
    ENCODING_LIST = ("utf-8", "cp1252", "cp437")
    
    # conversion table for address labels to libpostal tags
    _ADDR_LABEL_TO_POSTAL = {'street_no' : 'house_number',
                            'street_name' : 'road',
                            'unit' : 'unit',
                            'city' : 'city',
                            'region' : 'state',
                            'country' : 'country',
                            'postal_code' : 'postal_code' }

    def __init__(self, address_parser=None, database_type=None):
        """
        Initializes Algorithm object.

        Args:
            address_parser (function): Address parsing function, accepts a string 
                as an argument.
            database_type (str): Content type string of database.
        """
        self.address_parser = address_parser
        self.database_type = database_type
        
        if self.database_type == "education":
            self.FIELD_LABEL = self._EDU_FACILITY_LABELS + self._GENERAL_LABELS
        elif self.database_type == "hospital":
            self.FIELD_LABEL = self._HOSPITAL_LABELS + self._GENERAL_LABELS
        elif self.database_type == "library":
            self.FIELD_LABEL = self._LIBRARY_LABELS + self._GENERAL_LABELS
        elif self.database_type == "fire_station":
            self.FIELD_LABEL = self._FIRE_STATION_LABELS + self._GENERAL_LABELS
        elif self.database_type == "business":
            self.FIELD_LABEL = self._BUSINESS_LABELS + self._GENERAL_LABELS
        else:
            self.FIELD_LABEL = None
            

    def char_encode_check(self, source):
        """
        Identifies the character encoding of a source by reading the metadata
        or by a heuristic test.
        
        Args:
            source (Source): Dataset abstraction.

        Returns:
            e (str): Python character encoding string.

        Raises:
            ValueError: Invalid encoding from source.
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
                    with open('./data/raw/' + source.local_fname, encoding=enc) as f:
                        for line in f:
                            pass
                    return enc
                except UnicodeDecodeError:
                    pass
            raise RuntimeError("Could not guess original character encoding.")


    ############################################
    # Support functions for the 'parse' method #
    ############################################

    def _generateFieldNames(self, keys):
        '''Generates headers (column names) for the target tabulated data.'''
        row = [k for k in keys]
        if "address_str" in row:
            ind = row.index("address_str")
            row.pop(ind)
            for atag in reversed(self.ADDR_FIELD_LABEL):
                row.insert(ind, atag)
        return row

    def _isRowEmpty(self, row):
        '''Checks if a row (dict) has no non-empty entries.'''
        for key in row:
            if row[key] != "":
                return False
        return True

    def _quick_scrub(self, entry):
        '''Reformats a string using regex and returns it.'''
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

    def clean(self, source):
        """
        A general dataset cleaning method.

        Note:
            This function may be deprecated in the future for a more modular
            approach to defining cleaning methods.

        Args:
            source (Source): Dataset abstraction.
        """
        error_flag = False
        
        with open(source.dirtypath, 'r') as dirty, \
             open(source.cleanpath, 'w') as clean, \
             open(source.cleanerror, 'w') as error:

            csvreader = csv.DictReader(dirty)
            csvwriter = csv.DictWriter(clean, fieldnames=csvreader.fieldnames, quoting=csv.QUOTE_MINIMAL)

            error_headers = ['ERROR'] + csvreader.fieldnames
            csverror = csv.DictWriter(error, fieldnames=error_headers, quoting=csv.QUOTE_MINIMAL)
            
            csvwriter.writeheader()
            csverror.writeheader()

            # hard-coded variables used in cleaning
            province_territory_shortlist = ["ab", "bc", "mb", "nb", "nl", "ns", "nt", "nu", "on", "pe", "qc", "sk", "yt"]
            
            long_to_short_map = {"alberta": "ab",
                                 "british columbia": "bc",
                                 "manitoba": "mb",
                                 "new brunswick": "nb",
                                 "newfoundland": "nl",
                                 "newfoundland and labrador": "nl",
                                 "nova scotia": "ns",
                                 "northwest territories": "nt",
                                 "nunavut": "nu",
                                 "ontario": "on",
                                 "prince edward island": "pe",
                                 "québec": "qc",
                                 "quebec": "qc",
                                 "saskatchewan": "sk",
                                 "yukon": "yt"}

            # cleaning begins at this loop
            for row in csvreader:
                # general field cleaning
                # clean postal codes and filter errors
                if 'postal_code' in csvreader.fieldnames and row['postal_code'] != '':
                    postal_code = row['postal_code']
                    postal_code = re.sub(r"\s+", "", postal_code)
                    postal_code = postal_code.upper()
                    row['postal_code'] = postal_code

                    # check string length
                    if len(postal_code) != 6:
                        row['ERROR'] = "postal_code:"
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
                        row['ERROR'] = "postal_code:"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                    # check structure
                    if not re.match(r'[A-Z][0-9][A-Z][0-9][A-Z][0-9]', postal_code):
                        row['ERROR'] = "postal_code"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                # clean city name
                if 'city' in csvreader.fieldnames and row['city'] != '':
                    city_name = row['city']
                    city_name = re.sub(r"[.,']", '', city_name)
                    row['city'] = city_name
                
                # clean province name and filter errors
                if 'region' in csvreader.fieldnames and row['region'] != '':
                    if row['region'] in province_territory_shortlist:
                        pass
                    elif row['region'] in long_to_short_map:
                        row['region'] = long_to_short_map[row['region']]
                    else:
                        row['ERROR'] = "region"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                # clean country name and filter errors
                if 'country' in csvreader.fieldnames and row['country'] != '':
                    if row['country'] in ["ca", "can", "canada"]:
                        row['country'] = "ca"
                    else:
                        row['ERROR'] = "country"
                        csverror.writerow(row)
                        error_flag = True
                        continue

                # clean street name (specifically, the type and direction)
                # by definition, no false positives are captured
                if 'street_name' in csvreader.fieldnames and row['street_name'] != '':
                    st_name = row['street_name']
                    
                    # remove punctuation
                    st_name = re.sub(r"[.,']", '', st_name)
                    # remove number suffixes
                    st_name = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', st_name)

                    direction_map = {"east": "e", "west": "w", "north": "n", "south": "s"}
                    for i in ("east", "west", "north", "south"):
                        if re.search(r'%s$' % i, st_name):
                            st_name = re.sub(r'%s$' % i, direction_map[i], st_name)
                            break
                    
                    row['street_name'] = st_name


                # business label cleaning
                if self.database_type == "business":
                    pass
                    
                # education label cleaning
                if self.database_type == "education":
                    pass
                    
                # hospital label cleaning
                if self.database_type == "hospital":
                    pass

                # library label cleaning
                if self.database_type == "library":
                    pass

                # fire station label cleaning
                if self.database_type == "fire_station":
                    pass
                
                csvwriter.writerow(row)
                    
        if error_flag == False:
            os.remove(source.cleanerror)
        os.remove(source.dirtypath)

        
class CSV_Algorithm(Algorithm):
    """
    Algorithm child class, accompanied with methods designed for data in CSV format.
    """
    def extract_labels(self, source):
        """
        Constructs a dictionary that stores tags exclusively used in a source file.

        Args:
            source (Source): Dataset abstraction.
        """
        metadata = source.metadata
        label_map = dict()
        for i in self.FIELD_LABEL:
            if i in metadata['variables'] and (not (i in self.ADDR_FIELD_LABEL)):
                label_map[i] = metadata['variables'][i]
            # short circuit evaluation
            elif ('address_tokens' in metadata['variables']) and (i in metadata['variables']['address_tokens']):
                label_map[i] = metadata['variables']['address_tokens'][i] 

        source.label_map = label_map


    def parse(self, source):
        """
        Parses a dataset in CSV format to transform into a standardized CSV format.

        Args:
            source (Source): Dataset abstraction.

        Raises:
            Exception: Requires external handling if caught.
        """
        if not hasattr(source, 'label_map'):
            source.log.error("Source object missing 'label_map', 'extract_labels' was not ran")
            raise ValueError("Source object missing 'label_map'")

        tags = source.label_map
        enc = self.char_encode_check(source)
        FILTER_FLAG = False
        PROVIDER_FLAG = False

        if 'filter' in source.metadata:
            FILTER_FLAG = True

        with open(source.dirtypath, 'r', encoding=enc) as csv_file_read, \
             open(source.dirtypath + '-temp', 'w', encoding="utf-8") as csv_file_write:
            # define column labels
            col_names = [t for t in tags]
            if 'provider' in source.metadata:
                col_names.append('provider')
                PROVIDER_FLAG = True
            col_labels = self._generateFieldNames(col_names)

            # define reader/writer
            csvreader = csv.DictReader(csv_file_read)
            csvwriter = csv.DictWriter(csv_file_write, col_labels, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            csvwriter.writeheader()
            
            try:
                for entity in csvreader:
                    row = dict()
                    # START FILTERING HERE
                    BOOL_FILTER = []
                    CONT_FLAG = False

                    if FILTER_FLAG:
                        for attr in source.metadata['filter']:
                            VALID_FILTER = False
                            reg_ex = source.metadata['filter'][attr]
                            if reg_ex.search(entity[attr]):
                                VALID_FILTER = True
                            BOOL_FILTER.append(VALID_FILTER)

                    for b in BOOL_FILTER:
                        if not b:
                            CONT_FLAG = True
                            break

                    if CONT_FLAG:
                        continue
                    
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
                            # decision: check if key is "address_str"
                            # depth: 2
                            # # #
                            if key != "address_str":
                                row[key] = entry
                            else:
                                ap_entry = self.address_parser.parse(entry)
                                # SUGGESTION: This for loop is exclusively for libpostal output.
                                # Perhaps it should be moved to the AddressParser object?
                                for afl in self.ADDR_FIELD_LABEL:
                                    if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                        ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                        row[afl] = ap_entry[ind][0]
                                    else:
                                        row[afl] = ""
                            continue
                        # # #
                        # decision: check if key is "address_str"
                        # depth: 1
                        # # #
                        if key == "address_str":
                            entry = entity[tags[key]]
                            entry = self._quick_scrub(entry)
                            ap_entry = self.address_parser.parse(entry)
                            # SUGGESTION: This for loop is exclusively for libpostal output.
                            # Perhaps it should be moved to the AddressParser object?
                            for afl in self.ADDR_FIELD_LABEL:
                                if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                    ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                    row[afl] = ap_entry[ind][0]
                                else:
                                    row[afl] = ""
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
                        row[key] = entry

                    if not self._isRowEmpty(row):
                        # add customized entries here (e.g. provider)
                        if PROVIDER_FLAG:
                            row['provider'] = source.metadata['provider']
                            
                        csvwriter.writerow(row)
            except:
                raise

        os.rename(source.dirtypath + '-temp', source.dirtypath)

        
    def csv_format_correction(self, source, data_encoding):
        """
        Deletes rows of CSV datasets that have a number of entries not agreeing 
        with the total number of columns. Additionally removes a byte order mark 
        if it exists.

        Args:
            source (Source): Dataset abstraction.
            data_encoding (str): Data character encoding.
        """
        error_flag = False

        path = ''
        if source.prepath == None:
            path = source.rawpath
        else:
            path = source.prepath
        
        with open(path, 'r', encoding=data_encoding) as raw, \
             open(source.dirtypath, 'w', encoding=data_encoding) as dirty, \
             open(source.dirtyerror, 'w', encoding=data_encoding) as error:
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
                        source.log.error("Missing or too many entries on line %s" % line)
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
            os.remove(source.dirtyerror)


class XML_Algorithm(Algorithm):
    """
    Algorithm child class, accompanied with methods designed for data in XML format.
    """

    def extract_labels(self, source):
        """
        Constructs a dictionary that stores tags exclusively used in a source file. 
        Since datasets in XML format require a header tag in its source file, the 
        labels must be reformatted to XPath expressions.

        Args:
            source (Source): Dataset abstraction.
        """
        metadata = source.metadata
        label_map = dict()
        # append existing data using XPath expressions (for parsing)
        for i in self.FIELD_LABEL:
            if i in metadata['variables'] and (not (i in self.ADDR_FIELD_LABEL)) and i != 'address_tokens':
                if isinstance(metadata['variables'][i], list):
                    label_map[i] = []
                    for t in metadata['variables'][i]:
                        label_map[i].append(".//" + t)
                else:
                    label_map[i] = ".//" + metadata['variables'][i]
            # short circuit evaluation
            elif ('address_tokens' in metadata['variables']) and (i in metadata['variables']['address_tokens']):
                # note that the labels have to map to XPath expressions
                label_map[i] = ".//" + metadata['variables']['address_tokens'][i]

        source.label_map = label_map


    def parse(self, source):
        """
        Parses a dataset in XML format to transform into a standardized CSV format.

        Args:
            source (Source): Dataset abstraction.
        """
        if not hasattr(source, 'label_map'):
            raise ValueError("Source object missing 'label_map', 'extract_labels' was not ran.")

        path = ''
        if source.prepath == None:
            path = source.rawpath
        else:
            path = source.prepath

        tags = source.label_map
        header = source.metadata['header']
        enc = self.char_encode_check(source)
        FILTER_FLAG = False
        PROVIDER_FLAG = False

        if 'filter' in source.metadata:
            FILTER_FLAG = True
        
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(path, parser=xmlp)
        root = tree.getroot()

        with open(source.dirtypath, 'w', encoding="utf-8") as csvfile:
            # write the initial row which identifies each column
            col_names = [t for t in tags]
            if 'provider' in source.metadata:
                col_names.append('provider')
                PROVIDER_FLAG = True
            col_labels = self._generateFieldNames(col_names)

            csvwriter = csv.DictWriter(csvfile, col_labels, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csvwriter.writeheader()

            for element in root.iter(header):
                row = dict()
                # START FILTERING HERE
                BOOL_FILTER = []
                CONT_FLAG = False
                if FILTER_FLAG:
                    for attr in source.metadata['filter']:
                        VALID_FILTER = False
                        reg_ex = source.metadata['filter'][attr]
                        el = element.find(".//" + attr)
                        el = self._xml_empty_element_handler(el)
                        if reg_ex.search(el):
                            VALID_FILTER = True
                        BOOL_FILTER.append(VALID_FILTER)

                for b in BOOL_FILTER:
                    if not b:
                        CONT_FLAG = True
                        break

                if CONT_FLAG:
                    continue
                    
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
                        # decision: check if key is "address_str"
                        # depth: 2
                        # # #
                        if key != "address_str":
                            row[key] = entry
                        else:
                            ap_entry = self.address_parser.parse(entry)
                            # SUGGESTION: This for loop is exclusively for libpostal output.
                            # Perhaps it should be moved to the AddressParser object?
                            for afl in self.ADDR_FIELD_LABEL:
                                if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                    ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                    row[afl] = ap_entry[ind][0]
                                else:
                                    row[afl] = ""
                        continue
                    # # #
                    # decision: check if key is "address_str"
                    # depth: 1
                    # # #
                    if key == "address_str":
                        entry = element.find(tags[key])
                        entry = self._xml_empty_element_handler(entry)
                        entry = self._quick_scrub(entry)
                        ap_entry = self.address_parser.parse(entry)
                        # SUGGESTION: This for loop is exclusively for libpostal output.
                        # Perhaps it should be moved to the AddressParser object?
                        for afl in self.ADDR_FIELD_LABEL:
                            if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                                ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                                row[afl] = ap_entry[ind][0]
                            else:
                                row[afl] = ""
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
                    row[key] = self._quick_scrub(subel_content)
                    
                if not self._isRowEmpty(row):
                    # add customized entries here (e.g. provider)
                    if PROVIDER_FLAG:
                        row['provider'] = source.metadata['provider']
                        
                    csvwriter.writerow(row)


    def _xml_empty_element_handler(self, element):
        """
        The xml.etree module returns 'None' for text of empty-element tags. Moreover, 
        if the element cannot be found, the element is None. This function is defined 
        to handle these cases.

        Args:
            element (?): A node in the XML tree.

        Returns:
            str: Empty string if missing or empty tag, otherwise element.text.
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
    Source dataset class. Abstracts a dataset by storing metadata involving the data 
    file (format, name, etc.) and structure (XML headers, CSV column names, etc.). 
    Dynamic information is also included, such as the paths of the raw data, dirty
    and clean tabulated data.

    Attributes:
        srcpath (str): Source file path.
        metadata (dict): Source file JSON dumps.
        local_fname (str): Data file name (not path!).
        default_paths (bool): Allow Source.parse() to assign default paths to
            the path attributes described below
        rawpath (str): Raw data path (in './data/raw/').
        dirtypath (str): Dirty tabulated data path (in './data/dirty/').
        cleanpath (str): Clean tabulated data path (in './data/clean/').
        label_map (dict): Mapping of standardized labels (in Algorithm) to
            the raw datasets labels, obtained from self.metadata.
        log (Logger): Logger with self.local_fname as its name.
    """
    def __init__(self, path,
                 default_paths=True,
                 pre_flag=False,
                 post_flag=False,
                 no_fetch_flag=True,
                 no_extract_flag=True):
        """
        Initializes a new source file object.

        Raises:
            OSError: Path (of source file) does not exist.
        """
        if not os.path.exists(path):
            raise OSError('Path "%s" does not exist.' % path)
        self.srcpath = path
        with open(path) as f:
            self.metadata = json.load(f)

        self.default_paths = default_paths
        
        # determined by command line arguments
        self.pre_flag = pre_flag
        self.post_flag = post_flag
        self.no_fetch_flag = no_fetch_flag
        self.no_extract_flag = no_extract_flag
        
        # determined during parsing
        self.local_fname = None
        self.rawpath = None
        self.prepath = None
        self.prepath_temp = None
        self.dirtypath = None
        self.cleanpath = None
        self.dirtyerror = None
        self.cleanerror = None
        
        self.label_map = None

        self.log = None

    def parse(self):
        """
        Parses the source file to check correction of syntax.

        Raises:
            LookupError: Missing tag.
            ValueError: Incorrect entry or combination or entries, such as having
                an 'address_tokens' and 'address_str' tag will raise this error since they 
                cannot both be used in a source file.
            TypeError: Incorrect JSON type for a tag.
            OSError: Path for pre or post processing scripts not found.
        """
        # required tags
        if 'format' not in self.metadata:
            raise LookupError("'format' tag is missing.")
        if 'localfile' not in self.metadata:
            raise LookupError("'localfile' tag is missing.")
        if 'variables' not in self.metadata:
            raise LookupError("'variables' tag is missing.")
        if 'database_type' not in self.metadata:
            raise LookupError("'database_type' tag is missing.")

        # required tag types
        if not isinstance(self.metadata['format'], str):
            raise TypeError("'format' must be a string.")
        if not isinstance(self.metadata['localfile'], str):
            raise TypeError("'localfile' must be a string.")
        if not isinstance(self.metadata['variables'], dict):
            raise TypeError("'variables' must be an object.")
        if not isinstance(self.metadata['database_type'], str):
            raise TypeError("'database_type' must be a string.")

        # required formats
        if (self.metadata['format'] != 'xml') and (self.metadata['format'] != 'csv'):
            raise ValueError("Unsupported data format '" + self.metadata['format'] + "'")

        # required database types
        if (self.metadata['database_type'] != 'business') and \
	   (self.metadata['database_type'] != 'hospital') and \
	   (self.metadata['database_type'] != 'library') and \
           (self.metadata['database_type'] != 'fire_station') and \
           (self.metadata['database_type'] != 'education'):
            raise ValueError("Unsupported database type '" + self.metadata['database_type'] + "'")

        # OPTIONAL TAGS
        
        # required header if format is not csv
        if (self.metadata['format'] != 'csv') and ('header' not in self.metadata):
            raise LookupError("'header' tag missing for format " + self.metadata['format'])

        if (self.metadata['format'] != 'csv') and ('header' in self.metadata) and (not isinstance(self.metadata['header'], str)):
            raise TypeError("'header' must be a string.")

        if 'provider' in self.metadata and (not isinstance(self.metadata['provider'], str)):
            raise TypeError("'provider' must be a string.")

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
                raise OSError('Preprocessing script "%s" does not exist.' % self.metadata['pre'])
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
                raise OSError('Postprocessing script "%s" does not exist.' % self.metadata['post'])
            elif isinstance(self.metadata['post'], list):
                for script_path in self.metadata['post']:
                    if not os.path.exists(script_path):
                        raise OSError('Postprocessing script "%s" does not exist.' % script_path)                    

        # filter contents check
        if 'filter' in self.metadata:
            if not isinstance(self.metadata['filter'], dict):
                raise TypeError("'filter' must be an object.")
            else:
                for attribute in self.metadata['filter']:
                    if not isinstance(self.metadata['filter'][attribute], str):
                        raise TypeError("Filter attribute '%s' must be a string (regex)." % attribute)
                    else:
                        attr_filter = self.metadata['filter'][attribute]
                        reg_ex = re.compile(attr_filter)
                        self.metadata['filter'][attribute] = reg_ex

        # check that both address_str and address_tokens are not in the source file
        if ('address_tokens' in self.metadata['variables']) and ('address_str' in self.metadata['variables']):
            raise ValueError("Cannot have both 'address_str' and 'address_tokens' tags in source file.")

        # verify address_tokens is an object
        if 'address_tokens' in self.metadata['variables'] and \
           not isinstance(self.metadata['variables']['address_tokens'], dict):
            raise TypeError("'address_tokens' tag must be an object.")

        # set local_fname, rawpath, dirtypath, and cleanpath values
        self.local_fname = self.metadata['localfile'].split(':')[0]
        self.rawpath = './data/raw/' + self.local_fname        

        if len(self.local_fname.split('.')) == 1:
            self.dirtypath = './data/dirty/dirty-' + self.local_fname + ".csv"
            self.dirtyerror = './data/dirty/err-dirty-' + self.local_fname + ".csv"
            self.cleanpath = './data/clean/clean-' + self.local_fname + ".csv"
            self.cleanerror = './data/clean/err-clean-' + self.local_fname + ".csv"
        else:
            self.dirtypath = './data/dirty/dirty-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.dirtyerror = './data/dirty/err-dirty-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.cleanpath = './data/clean/clean-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.cleanerror = './data/clean/err-clean-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"

        if 'pre' in self.metadata: # note: preprocessing script existence is checked before this step
            self.prepath = './data/pre/pre-' + self.local_fname
            self.prepath_temp = './data/pre/pre-temp-' + self.local_fname

        # check entire source to make sure correct keys are being used
        for i in self.metadata:
            root_layer = ('localfile', 'localarchive', 'url', 'format', 'database_type',
                          'compression', 'encoding', 'pre', 'post', 'header', 'variables',
                          'filter', 'provider')
            if i not in root_layer:
                raise ValueError("Invalid key in root_layer '%s' in source file" % i)

        for i in self.metadata['variables']:
            variables_layer = ('address_str', 'address_tokens', 'phone', 'fax', 'email', 'website', 'tollfree',
                          'longitude', 'latitude')

            if self.metadata['database_type'] == 'business':
                bus_layer = ('legal_name', 'trade_name', 'business_type', 'business_no', 'bus_desc',
                             'licence_type', 'licence_no', 'start_date', 'closure_date', 'active',
                             'no_emp', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                             'home_bus', 'munic_bus', 'nonres_bus',
                             'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                             'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                             'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2')

                if not (i in variables_layer or i in bus_layer):
                    raise ValueError("Invalid key in bus_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'education':
                edu_layer = ('institution_name', 'institution_type', 'ins_code', 'education_level', 'board_name',
                            'board_code', 'school_yr', 'range', 'isced010', 'isced020', 'isced1',
                            'isced2', 'isced3', 'isced4+')
                if not (i in variables_layer or i in edu_layer):
                    raise ValueError("Invalid key in edu_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'library':
                lib_layer = ('library_name','library_type','library_board')
                if not (i in variables_layer or i in lib_layer):
                    raise ValueError("Invalid key in lib_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'hospital':
                hosp_layer = ('hospital_name','hospital_type','health_authority')
                if not (i in variables_layer or i in hosp_layer):
                    raise ValueError("Invalid key in hosp_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'fire_station':
                fire_layer = ('fire_station_name')
                if not (i in variables_layer or i in fire_layer):
                    raise ValueError("Invalid key in fire_layer '%s' in source file" % i)

        if 'address_tokens' in self.metadata['variables']:
            address_layer = ('street_no', 'street_name', 'unit', 'city', 'region', 'country', 'postal_code')
            for i in self.metadata['variables']['address_tokens']:
                if i not in address_layer:
                    raise ValueError("Invalid key in address_layer '%s' in source file" % i)

        self.log = logging.getLogger(self.local_fname)

                
    def fetch_url(self):
        """
        Downloads a dataset by fetching its URL and writing to the raw directory 
        (currently './data/raw').
        """
        if self.no_fetch_flag == True:
            return False
        
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
                with open('./data/raw/' + self.metadata['localarchive'], 'wb') as data:
                    data.write(content)
        else:
            with open('./data/raw/' + self.metadata['localfile'], 'wb') as data:
                data.write(content)

        return True

    def archive_extraction(self):
        """
        Extracts data from an archive downloaded in the raw directory ('./data/raw'), 
        renaming the file if indicated by the source file.
        """
        if self.no_extract_flag == True:
            return False
        
        if self.metadata['compression'] == "zip":
            with ZipFile('./data/raw/' + self.metadata['localarchive'], 'r') as zip_file:
                archive_fname = self.metadata['localfile'].split(':')
                if len(archive_fname) == 1:
                    zip_file.extract(archive_fname[0], './data/raw/')
                else:
                    zip_file.extract(archive_fname[1], './data/raw/')
                    os.rename('./data/raw/' + archive_fname[1], './data/raw/' + self.local_fname)

        return True

if __name__ == "__main__":
    # reserved for debugging
    pass
