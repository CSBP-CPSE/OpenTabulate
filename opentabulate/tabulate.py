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
    _GENERAL_LABELS = ('full_addr', 'street_no', 'street_name', 'postcode', 'unit', 'city', 'prov/terr', 'country',
                       'comdist', 'region',
                       'longitude', 'latitude',
                       'phone', 'fax', 'email', 'website', 'tollfree','hours', 'county')

    # business data labels
    _BUSINESS_LABELS = ('bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc',
                        'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active',
                        'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                        'home_bus', 'munic_bus', 'nonres_bus',
                        'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                        'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                        'naics_desc',
                        'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2',
                        'facebook', 'twitter', 'linkedin', 'youtube', 'instagram')

    # education data labels
    _EDU_FACILITY_LABELS = ('ins_name', 'ins_type', 'ins_code', 'edu_level', 'board_name',
                            'board_code', 'school_yr', 'range', 'isced010', 'isced020', 'isced1',
                            'isced2', 'isced3', 'isced4+')

    # hospital data labels
    _HOSPITAL_LABELS = ('hospital_name','hospital_type','health_authority')

    # hospital data labels
    _LIBRARY_LABELS = ('library_name','library_type','library_board')

    # fire station labels
    _FIRE_STATION_LABELS = ('fire_stn_name',)

    # supported address field labels
    # note that the labels are ordered to conform to the Canada Post mailing address standard
    ADDR_FIELD_LABEL = ('unit', 'street_no', 'street_name', 'city', 'prov/terr', 'country', 'postcode')

    # supported encodings (as defined in Python standard library)
    ENCODING_LIST = ("utf-8", "cp1252", "cp437")
    
    # conversion table for address labels to libpostal tags
    _ADDR_LABEL_TO_POSTAL = {'street_no' : 'house_number',
                            'street_name' : 'road',
                            'unit' : 'unit',
                            'city' : 'city',
                            'prov/terr' : 'state',
                            'country' : 'country',
                            'postcode' : 'postcode' }

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
        '''Generates headers (column names) for the target tabulated data.'''
        row = [t for t in tags]
        if "full_addr" in row:
            ind = row.index("full_addr")
            row.pop(ind)
            for atag in reversed(self.ADDR_FIELD_LABEL):
                row.insert(ind, atag)
        return row

    def _isRowEmpty(self, row):
        '''Checks if a row has no non-empty entries.'''
        for element in row:
            if element != "":
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
            csvwriter = csv.DictWriter(clean, fieldnames=csvreader.fieldnames, quoting=csv.QUOTE_ALL)

            error_headers = ['ERROR'] + csvreader.fieldnames
            csverror = csv.DictWriter(error, fieldnames=error_headers, quoting=csv.QUOTE_ALL)
            
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

                # clean city name
                if 'city' in csvreader.fieldnames and row['city'] != '':
                    city_name = row['city']
                    city_name = re.sub(r"[.,']", '', city_name)
                    row['city'] = city_name
                
                # clean province name and filter errors
                if 'prov/terr' in csvreader.fieldnames and row['prov/terr'] != '':
                    if row['prov/terr'] in province_territory_shortlist:
                        pass
                    elif row['prov/terr'] in long_to_short_map:
                        row['prov/terr'] = long_to_short_map[row['prov/terr']]
                    else:
                        row['ERROR'] = "prov/terr"
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

        Raises:
            Exception: Requires external handling if caught.
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
            source (Source): Dataset abstraction.
        """
        if not hasattr(source, 'label_map'):
            source.log.error("Source object missing 'label_map', 'extract_labels' was not ran")
            raise ValueError("Source object missing 'label_map'")

        tags = source.label_map
        enc = self.char_encode_check(source)
        FILTER_FLAG = False

        if 'filter' in source.metadata:
            FILTER_FLAG = True

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

        if 'filter' in source.metadata:
            FILTER_FLAG = True
        
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(path, parser=xmlp)
        root = tree.getroot()

        with open(source.dirtypath, 'w', encoding="utf-8") as csvfile:
            
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            # write the initial row which identifies each column
            col_labels = self._generateFirstRow(tags)
            csvwriter.writerow(col_labels)

            for element in root.iter(header):
                row = []
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
        rawpath (str): Raw data path (in './pddir/raw/').
        dirtypath (str): Dirty tabulated data path (in './pddir/dirty/').
        cleanpath (str): Clean tabulated data path (in './pddir/clean/').
        label_map (dict): Mapping of standardized labels (in Algorithm) to
            the raw datasets labels, obtained from self.metadata.
        log (Logger): Logger with self.local_fname as its name.
    """
    def __init__(self, path, pre_flag=False, post_flag=False, no_fetch_flag=True, \
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
                an 'address' and 'full_addr' tag will raise this error since they 
                cannot both be used in a source file.
            TypeError: Incorrect JSON type for a tag.
            OSError: Path for pre or post processing scripts not found.
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
            self.dirtypath = './pddir/dirty/dirty-' + self.local_fname + ".csv"
            self.dirtyerror = './pddir/dirty/err-dirty-' + self.local_fname + ".csv"
            self.cleanpath = './pddir/clean/clean-' + self.local_fname + ".csv"
            self.cleanerror = './pddir/clean/err-clean-' + self.local_fname + ".csv"
        else:
            self.dirtypath = './pddir/dirty/dirty-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.dirtyerror = './pddir/dirty/err-dirty-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.cleanpath = './pddir/clean/clean-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"
            self.cleanerror = './pddir/clean/err-clean-' + '.'.join(str(x) for x in self.local_fname.split('.')[:-1]) + ".csv"

        if 'pre' in self.metadata: # note: preprocessing script existence is checked before this step
            self.prepath = './pddir/pre/pre-' + self.local_fname
            self.prepath_temp = './pddir/pre/pre-temp-' + self.local_fname

        # check entire source to make sure correct keys are being used
        for i in self.metadata:
            root_layer = ('localfile', 'localarchive', 'url', 'format', 'database_type',
                           'compression', 'encoding', 'pre', 'post', 'header', 'info', 'filter')
            if i not in root_layer:
                raise ValueError("Invalid key in root_layer '%s' in source file" % i)

        for i in self.metadata['info']:
            info_layer = ('full_addr', 'address', 'phone', 'fax', 'email', 'website', 'tollfree',
                          'comdist', 'region', 'longitude', 'latitude', 'hours', 'county')

            if self.metadata['database_type'] == 'business':
                bus_layer = ('bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc',
                             'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active',
                             'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                             'home_bus', 'munic_bus', 'nonres_bus',
                             'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                             'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                             'naics_desc',
                             'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2',
                             'facebook', 'twitter', 'linkedin', 'youtube', 'instagram')
                if not (i in info_layer or i in bus_layer):
                    raise ValueError("Invalid key in bus_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'education':
                edu_layer = ('ins_name', 'ins_type', 'ins_code', 'edu_level', 'board_name',
                            'board_code', 'school_yr', 'range', 'isced010', 'isced020', 'isced1',
                            'isced2', 'isced3', 'isced4+')
                if not (i in info_layer or i in edu_layer):
                    raise ValueError("Invalid key in edu_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'library':
                lib_layer = ('library_name','library_type','library_board')
                if not (i in info_layer or i in lib_layer):
                    raise ValueError("Invalid key in lib_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'hospital':
                hosp_layer = ('hospital_name','hospital_type','health_authority')
                if not (i in info_layer or i in hosp_layer):
                    raise ValueError("Invalid key in hosp_layer '%s' in source file" % i)

            elif self.metadata['database_type'] == 'fire_station':
                fire_layer = ('fire_stn_name')
                if not (i in info_layer or i in fire_layer):
                    raise ValueError("Invalid key in fire_layer '%s' in source file" % i)

        if 'address' in self.metadata['info']:
            address_layer = ('street_no', 'street_name', 'unit', 'city', 'prov/terr', 'country', 'postcode')
            for i in self.metadata['info']['address']:
                if i not in address_layer:
                    raise ValueError("Invalid key in address_layer '%s' in source file" % i)
            
        self.log = logging.getLogger(self.local_fname)

                
    def fetch_url(self):
        """
        Downloads a dataset by fetching its URL and writing to the raw directory 
        (currently './pddir/raw').
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
                with open('./pddir/raw/' + self.metadata['localarchive'], 'wb') as data:
                    data.write(content)
        else:
            with open('./pddir/raw/' + self.metadata['localfile'], 'wb') as data:
                data.write(content)

        return True

    def archive_extraction(self):
        """
        Extracts data from an archive downloaded in the raw directory ('./pddir/raw'), 
        renaming the file if indicated by the source file.
        """
        if self.no_extract_flag == True:
            return False
        
        if self.metadata['compression'] == "zip":
            with ZipFile('./pddir/raw/' + self.metadata['localarchive'], 'r') as zip_file:
                archive_fname = self.metadata['localfile'].split(':')
                if len(archive_fname) == 1:
                    zip_file.extract(archive_fname[0], './pddir/raw/')
                else:
                    zip_file.extract(archive_fname[1], './pddir/raw/')
                    os.rename('./pddir/raw/' + archive_fname[1], './pddir/raw/' + self.local_fname)

        return True

if __name__ == "__main__":
    # reserved for debugging
    pass
