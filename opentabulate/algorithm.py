# -*- coding: utf-8 -*-
"""
Tabulation methods API.

This module defines the core functionality of OpenTabulate, which contains the 
Algorithm class and its children, which give methods for parsing, processing, and 
reformatting microdata into CSV format.

The child classes correspond to the different data formats handled (e.g. CSV, XML).


Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

# Code comment prefixes: 
# IMPORTANT, SUGGESTION, DEBUG, TESTING, DEPRECATED
# ---

# SUGGESTION: Handle "with open" so that Algorithm parsing methods receive file descriptors
# rather than paths?

###########
# MODULES #
###########

import csv
import operator
import os
import re
from copy import deepcopy
from xml.etree import ElementTree

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
    _GENERAL_LABELS = ('address_str_parse', 'address_str',
                       'street_no', 'street_name', 'postal_code', 'unit', 'city', 'province', 'country',
                       'longitude', 'latitude',
                       'phone', 'fax', 'email', 'website', 'tollfree'
    ) + ('comdist', 'region', 'hours', 'county')

    # business data labels
    _BUSINESS_LABELS = ('legal_name', 'trade_name', 'business_type', 'business_no', 'bus_desc',
                        'licence_type', 'licence_no', 'start_date', 'closure_date', 'active',
                        'no_emp', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                        'home_bus', 'munic_bus', 'nonres_bus',
                        'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                        'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                        'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2'
    ) + ('no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
         'home_bus', 'munic_bus', 'nonres_bus', 'naics_desc',
         'facebook', 'twitter', 'linkedin', 'youtube', 'instagram')

    # education data labels
    _EDU_FACILITY_LABELS = ('institution_name', 'institution_type', 'ins_code', 'education_level', 'board_name',
                            'board_code', 'school_yr', 'range', 'isced010', 'isced020', 'isced1',
                            'isced2', 'isced3', 'isced4+'
    ) + ('ins_code', 'school_yr')

    # hospital data labels
    _HOSPITAL_LABELS = ('hospital_name','hospital_type','health_authority')

    # hospital data labels
    _LIBRARY_LABELS = ('library_name','library_type','library_board')

    # fire station labels
    _FIRE_STATION_LABELS = ('fire_station_name',)

    # supported address field labels
    # note that the labels are ordered to conform to the Canada Post mailing address standard
    ADDR_FIELD_LABEL = ('unit', 'street_no', 'street_name', 'city', 'province', 'country', 'postal_code')

    # supported encodings (as defined in Python standard library)
    ENCODING_LIST = ("utf-8", "cp1252", "cp437")
    
    # conversion table for address labels to libpostal tags
    _ADDR_LABEL_TO_POSTAL = {'street_no' : 'house_number',
                             'street_name' : 'road',
                             'unit' : 'unit',
                             'city' : 'city',
                             'province' : 'state',
                             'country' : 'country',
                             'postal_code' : 'postcode' }

    def __init__(self, source=None, address_parser=None):
        """
        Initializes Algorithm object.

        Args:
            source (Source): Dataset abstraction.
            address_parser (function): Address parsing function, accepts a string 
                as an argument.
        """
        self.source = source
        self.address_parser = address_parser

        if source is not None:
            self.database_type = source.metadata['database_type']

            self.FILTER_FLAG = True if 'filter' in source.metadata else False    
            self.PROVIDER_FLAG = True if 'provider' in source.metadata else False

            if self.PROVIDER_FLAG == False:
                source.logger.warning("No 'provider' flag given")

            self.FORCE_REGEXP = re.compile('force:.*')

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
            

    def char_encode_check(self):
        """
        Identifies the character encoding of a source by reading the metadata
        or by a heuristic test.
        
        Returns:
            e (str): Python character encoding string.

        Raises:
            ValueError: Invalid encoding from source.
            RunTimeError: Character encoding test failed.
        """
        metadata = self.source.metadata
        if 'encoding' in metadata:
            data_enc = metadata['encoding']
            if data_enc in self.ENCODING_LIST:
                return data_enc
            else:
                raise ValueError(data_enc + " is not a valid encoding.")
        else:
            for enc in self.ENCODING_LIST:
                try:
                    with open(self.source.rawpath, encoding=enc) as f:
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
        if "address_str_parse" in row:
            ind = row.index("address_str_parse")
            row.pop(ind)
            for atag in reversed(self.ADDR_FIELD_LABEL):
                row.insert(ind, atag)
        return row

    def _isRowEmpty(self, row):
        """
        Checks if a row (dict) has no non-empty entries.
        
        Raises:
            AssertionError: Row value is not a string.
        """
        for key in row:
            if row[key] != "":
                assert isinstance(row[key], str), 'Row value is not a string'
                return False
        return True

    def _quickScrub(self, entry):
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

    def _rowParseAddress(self, row, entry):
        """
        Parse the address of the string 'entry' and add the values to the 
        OrderedDict object 'row'.

        Args:
            row (dict): CSV row for processed output.
            entry (str): Address string.
        """
        ap_entry = self.address_parser.parse(entry)
        # SUGGESTION: This for loop is exclusively for libpostal output.
        # Perhaps it should be moved to the AddressParser object?
        for afl in self.ADDR_FIELD_LABEL:
            if self._ADDR_LABEL_TO_POSTAL[afl] in [x[1] for x in ap_entry]:
                ind = list(map(operator.itemgetter(1), ap_entry)).index(self._ADDR_LABEL_TO_POSTAL[afl])
                row[afl] = ap_entry[ind][0]
            else:
                row[afl] = ""

        ap_entry = self.address_parser.parse(entry)
        
    def _isForceValue(self, value):
        """
        Returns:
            (bool): if 'value' is of the form 'force:*'
        """
        return bool(self.FORCE_REGEXP.match(value))

    
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
                if 'province' in csvreader.fieldnames and row['province'] != '':
                    if row['province'] in province_territory_shortlist:
                        pass
                    elif row['province'] in long_to_short_map:
                        row['province'] = long_to_short_map[row['province']]
                    else:
                        row['ERROR'] = "province"
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
    def extract_labels(self):
        """
        Constructs a dictionary that stores tags exclusively used in a source file.
        """
        metadata = self.source.metadata
        label_map = dict()
        for i in self.FIELD_LABEL:
            if i in metadata['schema'] and (not (i in self.ADDR_FIELD_LABEL)):
                label_map[i] = metadata['schema'][i]
                # short circuit evaluation
            elif ('address_tokens' in metadata['schema']) and (i in metadata['schema']['address_tokens']):
                label_map[i] = metadata['schema']['address_tokens'][i] 

        self.label_map = label_map


    def parse(self):
        """
        Parses a dataset in CSV format to transform into a standardized CSV format.

        Raises:
            Exception: Requires external handling if caught.
        """
        if not hasattr(self, 'label_map'):
            self.source.logger.error("Missing 'label_map', 'extract_labels' was not ran")
            raise ValueError("Missing 'label_map' for parsing")

        tags = deepcopy(self.label_map)
        enc = self.char_encode_check()

        if self.source.prepath == None:
            path = self.source.rawpath
        else:
            path = self.source.prepath
        
        with open(path, 'r', encoding=enc) as csv_file_read, \
             open(self.source.dirtypath, 'w', encoding="utf-8") as csv_file_write:
            # define column labels
            col_names = [t for t in tags]
            if self.PROVIDER_FLAG:
                col_names.append('provider')

            col_labels = self._generateFieldNames(col_names)

            # define reader/writer
            csvreader = csv.DictReader(
                csv_file_read,
                delimiter=self.source.metadata['format']['delimiter'],
                quotechar=self.source.metadata['format']['quote']
            )
            csvwriter = csv.DictWriter(
                csv_file_write,
                col_labels,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            # remove byte order mark (BOM)
            csvreader.fieldnames[0] = re.sub(r"^\ufeff(.+)", r"\1", csvreader.fieldnames[0])
            no_columns = len(csvreader.fieldnames)
            
            csvwriter.writeheader()
            
            for entity in csvreader:
                row = dict()

                # if there are more or less row entries than number of columns, throw error
                if len(entity) != no_columns:
                    self.source.logger.error(
                        "Incorrect number of entries on line %s" % csvreader.line_num
                    )
                    raise csv.Error
                    
                # filter entry
                if not self._csv_keep_entry(entity):
                    continue
                    
                for key in tags:
                    # --%-- check if tags[key] is a JSON array --%--
                    if isinstance(tags[key], list):
                        components = []
                        for subentry in tags[key]:
                            # is 'i' a 'force' entry?
                            if self._isForceValue(subentry):
                                components.append(subentry.split(':')[1])
                            else:
                                components.append(entity[subentry])

                            entry = ' '.join(components)
                            entry = self._quickScrub(entry)
                            # --%-- check if key is "address_str_parse" --%--
                            if key != "address_str_parse":
                                row[key] = entry
                            else:
                                self._rowParseAddress(row, entry)
                                
                        continue
                            
                    # --%-- check if key is 'address_str_parse' --%--
                    if key == "address_str_parse":
                        # SUGGESTION: get source.py to error handle when 'address_str_parse' value is 'force'
                        entry = entity[tags[key]]
                        entry = self._quickScrub(entry)
                        self._rowParseAddress(row, entry)
                        continue

                    # --%-- all other cases handled here --%--
                    # is 'tags[key]' a 'force' entry?
                    if self._isForceValue(tags[key]):
                        entry = tags[key].split(':')[1]
                    else:
                        entry = entity[tags[key]]

                    row[key] = self._quickScrub(entry)
                                                    
                if not self._isRowEmpty(row):
                    # add customized entries here (e.g. provider)
                    if self.PROVIDER_FLAG:
                        row['provider'] = self.source.metadata['provider']
                            
                    csvwriter.writerow(row)
            

    def _csv_keep_entry(self, entity):
        """
        Regular expression filtering implementation.
        """
        if not self.FILTER_FLAG:
            # keep entries if no filter flag is used
            return True
        else:
            BOOL_MATCHES = []
            for attribute in self.source.metadata['filter']:
                match = False
                regexp = self.source.metadata['filter'][attribute]
                if regexp.search(entity[attribute]):
                    match = True
                BOOL_MATCHES.append(match)

            for var in BOOL_MATCHES:
                # if one of the matches failed, discard entry
                if not var:
                    return False
            # otherwise, keep entry
            return True


class XML_Algorithm(Algorithm):
    """
    Algorithm child class, accompanied with methods designed for data in XML format.
    """

    def extract_labels(self):
        """
        Constructs a dictionary that stores tags exclusively used in a source file. 
        Since datasets in XML format require a header tag in its source file, the 
        labels must be reformatted to XPath expressions.
        """
        metadata = self.source.metadata
        label_map = dict()
        # append existing data using XPath expressions (for parsing)
        for i in self.FIELD_LABEL:
            if i in metadata['schema'] and (not (i in self.ADDR_FIELD_LABEL)) and i != 'address_tokens':
                if isinstance(metadata['schema'][i], list):
                    label_map[i] = []
                    for t in metadata['schema'][i]:
                        label_map[i] = t if self._isForceValue(t) else (".//" + t)
                else:
                    val = metadata['schema'][i]
                    label_map[i] = val if self._isForceValue(val) else (".//" + val)
                    # short circuit evaluation
            elif ('address_tokens' in metadata['schema']) and (i in metadata['schema']['address_tokens']):
                # note that the labels have to map to XPath expressions
                val = metadata['schema']['address_tokens'][i]
                label_map[i] = val if self._isForceValue(val) else (".//" + val)

        self.label_map = label_map


    def parse(self):
        """
        Parses a dataset in XML format to transform into a standardized CSV format.
        """
        if not hasattr(self, 'label_map'):
            self.source.logger.error("Missing 'label_map', 'extract_labels' was not ran")
            raise ValueError("Missing 'label_map' for parsing")

        path = ''
        if self.source.prepath == None:
            path = self.source.rawpath
        else:
            path = self.source.prepath

        tags = deepcopy(self.label_map)
        header = self.source.metadata['format']['header']
        enc = self.char_encode_check()

        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(path, parser=xmlp)
        root = tree.getroot()

        with open(self.source.dirtypath, 'w', encoding="utf-8") as csvfile:
            # write the initial row which identifies each column
            col_names = [t for t in tags]
            if self.PROVIDER_FLAG:
                col_names.append('provider')
   
            col_labels = self._generateFieldNames(col_names)

            csvwriter = csv.DictWriter(
                csvfile,
                col_labels,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            csvwriter.writeheader()

            for element in root.iter(header):
                row = dict()
                
                # filter entry
                if not self._xml_keep_entry(element): 
                    continue
                
                for key in tags:
                    # --%-- check if tags[key] is a JSON array --%--
                    if isinstance(tags[key], list):
                        components = []
                        for subentry in tags[key]:
                            # is subentry a 'force' entry?
                            if self._isForceValue(subentry):
                                components.append(subentry.split(':')[1])
                            else:
                                subelement = element.find(subentry)
                                subelement = self._xml_empty_element_handler(subelement)
                                components.append(subelement)

                        entry = ' '.join(components)
                        entry = self._quickScrub(entry)
                        # --%-- check if key is "address_str_parse" --%--
                        if key != "address_str_parse":
                            row[key] = entry
                        else:
                            self._rowParseAddress(row, entry)
                            
                        continue

                    # --%-- check if key is 'address_str_parse' --%--
                    if key == "address_str_parse":
                        # SUGGESTION: get source.py to error handle when 'address_str_parse' value is 'force'
                        entry = element.find(tags[key])
                        entry = self._xml_empty_element_handler(entry)
                        entry = self._quickScrub(entry)
                        self._rowParseAddress(row, entry)
                        continue

                    # --%-- all other cases handled here --%--
                    # is 'tags[key]' a 'force' entry?
                    if self._isForceValue(tags[key]):
                        entry = tags[key].split(':')[1]
                    else:
                        entry = element.find(tags[key])
                        entry = self._xml_empty_element_handler(entry)
                        
                    row[key] = self._quickScrub(entry)
                        
                if not self._isRowEmpty(row):
                    # add customized entries here (e.g. provider)
                    if self.PROVIDER_FLAG:
                        row['provider'] = self.source.metadata['provider']
                        
                    csvwriter.writerow(row)


    def _xml_keep_entry(self, element):
        """
        Regular expression filtering implementation.
        """
        if not self.FILTER_FLAG:
            # keep entries if no filter flag is used
            return True
        else:
            BOOL_MATCHES = []
            for attribute in self.source.metadata['filter']:
                match = False
                regexp = self.source.metadata['filter'][attribute]
                el = element.find(".//" + attribute)
                el = self._xml_empty_element_handler(el)
                if regexp.search(el):
                    match = True
                BOOL_MATCHES.append(match)

            for var in BOOL_MATCHES:
                # if one of the matches failed, discard entry
                if not var:
                    return False
            # otherwise, keep entry
            return True

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
        if element is None: # SUGGESTION: add warnings or raise error if tags are missing
            return ''
        if not (element.text is None):
            return element.text
        else:
            return ''
