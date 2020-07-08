# -*- coding: utf-8 -*-
"""
Tabulation API.

This module defines the core functionality of OpenTabulate, which contains the 
Algorithm class and its children. The classes provide methods for parsing, 
processing and tabulating input data into CSV format.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

#######################
# MODULES AND IMPORTS #
#######################

import csv
import os
import re
from xml.etree import ElementTree

from opentabulate.main.config import SUPPORTED_ENCODINGS
from opentabulate.main.thread_exception import ThreadInterruptError

#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm():
    """
    Parent algorithm class for data processing.

    Attributes:
        source (Source): Dataset processing configuration and metadata.
        interrupt (threading.Event): Event to halt multi-threaded processing. 
        label_map (dict): Column name mapping to output CSV.
        FORCE_REGEXP (re.Pattern): Regular expression for 'force' values in source.

        OUTPUT_ENC_ERRORS (str): Flag for how to handle character encoding errors.
        FILTER_FLAG (bool): Flag for data filtering.
        PROVIDER_FLAG (bool): Flag for 'provider' column.
        ADD_INDEX (bool): Flag for 'idx' column.
        NO_WHITESPACE (bool): Flag for handling unnecessary whitespace (e.g. new lines,
            tabs, separation of words by multiple spaces)
        LOWERCASE (bool): Flag to whether or not the output is made lowercase.
    """
    def __init__(self, source=None, interrupt=None):
        """
        Initializes Algorithm object.

        Args:
            source (Source): Dataset abstraction.
            interrupt (threading.Event): Event to halt multi-threaded processing. 
        """
        self.source = source
        self.interrupt = interrupt
        self.label_map = None

        self.FORCE_REGEXP = re.compile('force:.*')

        # flags
        self.OUTPUT_ENC_ERRORS = None
        self.FILTER_FLAG = None
        self.PROVIDER_FLAG = None
        self.ADD_INDEX = None
        self.NO_WHITESPACE = None
        self.LOWERCASE = None

        if source is not None:
            # flags from source file metadata
            self.FILTER_FLAG = True if 'filter' in source.metadata else False    
            self.PROVIDER_FLAG = True if 'provider' in source.metadata else False

            self.OUTPUT_ENC_ERRORS = source.config.get('general', 'output_encoding_errors')

            if source.config is not None:
                # configuration or command line flags
                self.ADD_INDEX = True if source.config.getboolean('general', 'add_index') else False
                self.NO_WHITESPACE = True if source.config.getboolean('general', 'clean_whitespace') else False
                self.LOWERCASE = True if source.config.getboolean('general', 'lowercase_output') else False

            source.logger.debug("FILTER_FLAG set to %s" % self.FILTER_FLAG)
            source.logger.debug("PROVIDER_FLAG set to %s" % self.PROVIDER_FLAG)
            source.logger.debug("ADD_INDEX set to %s" % self.ADD_INDEX)
            source.logger.debug("NO_WHITESPACE set to %s" % self.NO_WHITESPACE)
            source.logger.debug("LOWERCASE set to %s" % self.LOWERCASE)
            source.logger.debug("OUTPUT_ENC_ERRORS set to %s" % self.OUTPUT_ENC_ERRORS)

    def char_encode_check(self):
        """
        Heuristic test to identify the character encoding of a source. Every
        line in the file is attempted to be decoded over a set of supported
        encodings in a fixed order. The first encoding that successfully
        decodes the entire file is taken to be its encoding for the tabulation
        step. Otherwise if all fail, then a RunTimeError is raised.
        
        Returns:
            e (str): Python character encoding string.

        Raises:
            ValueError: Invalid encoding from source.
            RunTimeError: Character encoding test failed.
            ThreadInterruptError: Interrupt event occurred in main thread.
        """
        metadata = self.source.metadata
        if 'encoding' in metadata:
            data_enc = metadata['encoding']
            if data_enc in SUPPORTED_ENCODINGS:
                return data_enc
            else:
                raise ValueError(data_enc + " is not a valid encoding.")
        else:
            for enc in SUPPORTED_ENCODINGS:
                try:
                    with open(self.source.input_path, encoding=enc) as f:
                        for _ in f:
                            if self.interrupt is not None and self.interrupt.is_set():
                                raise ThreadInterruptError("Interrupt event occurred.")
                    return enc
                except UnicodeDecodeError:
                    pass
            raise RuntimeError("Could not guess original character encoding.")


    ##############################################
    # Helper functions for the 'tabulate' method #
    ##############################################

    def _generateFieldNames(self, keys):
        """Generate column names for the target tabulated data."""
        return [k for k in keys]

    def _isRowEmpty(self, row):
        """
        Check if a row (dict) has no non-empty entries.
        
        Raises:
            AssertionError: Row value is not a string.
        """
        for key in row:
            if row[key] != "":
                assert isinstance(row[key], str), 'Row value is not a string'
                return False
        return True

    def _quickCleanEntry(self, entry):
        """Reformat a string using regex and return it."""
        if isinstance(entry, bytes):
            entry = entry.decode()

        if self.NO_WHITESPACE: # remove redundant [:space:] char class characters
            # since this includes removal of newlines, the next regexps are safe and
            # do not require the "DOTALL" flag
            entry = re.sub(r"\s+", " ", entry)
            # remove spaces occuring at the beginning and end of an entry
            entry = re.sub(r"^\s+([^\s].*)", r"\1", entry)
            entry = re.sub(r"(.*[^\s])\s+$", r"\1", entry)
            entry = re.sub(r"^\s+$", "", entry)

        if self.LOWERCASE: # make entries lowercase
            entry = entry.lower()
            
        return entry

    def _isForceValue(self, value):
        """Returns True if value contains the prefix 'force:'."""
        return bool(self.FORCE_REGEXP.match(value))
        

class CSV_Algorithm(Algorithm):
    """
    Algorithm child class designed to handle CSV formatted data.
    """
    def construct_label_map(self):
        """
        Constructs a dictionary from a column map that the 'tabulate' function uses to
        to reformat input data.
        """
        self.label_map = self.source.column_map

    def tabulate(self):
        """
        Parses a dataset in CSV format to transform into a standardized CSV format.

        Exceptions raised must be handled external to this module.

        Raises:
            ValueError: Label map for parsing data is missing.
            csv.Error: Incorrect format of CSV data
            ThreadInterruptError: Interrupt event occurred in main thread.
        """
        if not hasattr(self, 'label_map'):
            raise ValueError("Missing 'label_map' for parsing, 'construct_label_map' was not ran")

        tags = self.label_map
        enc = self.char_encode_check()

        with open(self.source.input_path, 'r', encoding=enc) as csv_file_read, \
             open(self.source.output_path, 'w',
                  encoding=self.source.config.get('general', 'target_encoding'),
                  errors=self.OUTPUT_ENC_ERRORS
             ) as csv_file_write:
            # define column labels
            fieldnames = self._generateFieldNames(tags)
            
            if self.PROVIDER_FLAG:
                fieldnames.append('provider')

            if self.ADD_INDEX:
                fieldnames.insert(0, 'idx')

            # define reader/writer
            csvreader = csv.DictReader(
                csv_file_read,
                delimiter=self.source.metadata['format']['delimiter'],
                quotechar=self.source.metadata['format']['quote']
            )
            csvwriter = csv.DictWriter(
                csv_file_write,
                fieldnames,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            # remove (possibly existing) byte order mark (BOM)
            csvreader.fieldnames[0] = re.sub(r"^\ufeff(.+)", r"\1", csvreader.fieldnames[0])
            no_columns = len(csvreader.fieldnames)
            
            csvwriter.writeheader()

            idx = 0
            
            for entity in csvreader:
                if self.interrupt is not None and self.interrupt.is_set():
                    raise ThreadInterruptError("Interrupt event occurred")

                row = dict()

                no_row_entries = 0
                for x in entity:
                    if entity[x] is not None:
                        no_row_entries += 1

                # if there are more or less row entries than number of columns, throw error
                if no_row_entries != no_columns:
                    raise csv.Error("Incorrect number of entries on line %s" % csvreader.line_num)
                    
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
                            entry = self._quickCleanEntry(entry)
                            
                        row[key] = entry
                        continue
                            
                    # --%-- all other cases handled here --%--
                    # is 'tags[key]' a 'force' entry?
                    if self._isForceValue(tags[key]):
                        entry = tags[key].split(':')[1]
                    else:
                        entry = entity[tags[key]]

                    row[key] = self._quickCleanEntry(entry)

                if not self._isRowEmpty(row):
                    # add customized entries here (e.g. provider)
                    if self.PROVIDER_FLAG:
                        row['provider'] = self.source.metadata['provider']

                    if self.ADD_INDEX:
                        row['idx'] = idx
                        idx += 1
                        
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
    Algorithm child class with methods designed to handle XML formatted data.
    """
    def construct_label_map(self):
        """
        Constructs a dictionary from a column map that the 'tabulate' function uses to
        to reformat input data. In this case (XML formatted data), the values in the
        column map must be converted to XPath expressions.
        """
        label_map = dict()
        # append existing data using XPath expressions (for parsing)
        for k in self.source.column_map:
            if isinstance(self.source.column_map[k], list):
                label_map[k] = list()
                for t in self.source.column_map[k]:
                    label_map[k].append(t if self._isForceValue(t) else (".//" + t))
            else:
                val = self.source.column_map[k]
                label_map[k] = val if self._isForceValue(val) else (".//" + val)
                    
        self.label_map = label_map


    def tabulate(self):
        """
        Parses a dataset in XML format to transform into a standardized CSV format.

        Exceptions raised must be handled external to this module.

        Raises:
            ValueError: Label map for parsing data is missing.
            ThreadInterruptError: Interrupt event occurred in main thread.
        """
        if not hasattr(self, 'label_map'):
            raise ValueError("Missing 'label_map' for parsing, 'construct_label_map' was not ran")

        tags = self.label_map
        header = self.source.metadata['format']['header']
        enc = self.char_encode_check()

        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse(self.source.input_path, parser=xmlp)
        root = tree.getroot()

        with open(self.source.output_path, 'w',
                  encoding=self.source.config.get('general', 'target_encoding'),
                  errors=self.OUTPUT_ENC_ERRORS
        ) as csvfile:
            # write the initial row which identifies each column
            fieldnames = self._generateFieldNames(tags)
            
            if self.PROVIDER_FLAG:
                fieldnames.append('provider')

            if self.ADD_INDEX:
                fieldnames.insert(0, 'idx')
   
            csvwriter = csv.DictWriter(
                csvfile,
                fieldnames,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            csvwriter.writeheader()

            idx = 0

            for head_element in root.iter(header):
                if self.interrupt is not None and self.interrupt.is_set():
                    raise ThreadInterruptError("Interrupt event occurred")

                row = dict()

                # filter entry
                if not self._xml_keep_entry(head_element):
                    continue
                
                for key in tags:
                    # --%-- check if tags[key] is a JSON array --%--
                    if isinstance(tags[key], list):
                        components = []
                        for val in tags[key]:
                            # is val a 'force' entry?
                            if self._isForceValue(val):
                                components.append(val.split(':')[1])
                            else:
                                assert val[:3] == './/'
                                tag_name = val[3:] # removes './/' prefix
                                subelement = head_element.find(val)
                                subelement = self._xml_is_element_missing(subelement, tag_name, head_element)
                                components.append(subelement)

                        entry = ' '.join(components)
                        row[key] = self._quickCleanEntry(entry)
                        continue

                    # --%-- all other cases handled here --%--
                    # is 'tags[key]' a 'force' entry?
                    if self._isForceValue(tags[key]):
                        entry = tags[key].split(':')[1]
                    else:
                        assert tags[key][:3] == './/'
                        tag_name = tags[key][3:] # removes './/' prefix
                        element = head_element.find(tags[key])
                        element = self._xml_is_element_missing(element, tag_name, head_element)
                        entry = element
                        
                    row[key] = self._quickCleanEntry(entry)
                        
                if not self._isRowEmpty(row):
                    # add customized entries here (e.g. provider)
                    if self.PROVIDER_FLAG:
                        row['provider'] = self.source.metadata['provider']

                    if self.ADD_INDEX:
                        row['idx'] = idx
                        idx += 1

                    csvwriter.writerow(row)


    def _xml_keep_entry(self, head_element):
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
                element = head_element.find(".//" + attribute)
                element = self._xml_is_element_missing(element, attribute, head_element)
                if regexp.search(element):
                    match = True
                BOOL_MATCHES.append(match)

            for var in BOOL_MATCHES:
                # if one of the matches failed, discard entry
                if not var:
                    return False
            # otherwise, keep entry
            return True

    def _xml_is_element_missing(self, element, tag_name, head_element):
        """
        The xml.etree module returns 'None' if there is no text in a tag. Moreover, if
        the element cannot be found, the element is None.

        Args:
            element (ElementTree.Element): Target node in XML tree.
            tag_name (str): Target tag name in tree parsing.
            head_element (ElementTree.Element): Header node in XML tree.

        Returns:
            str: Empty string if missing or empty tag, otherwise element.text.
        """
        if element is None:
            return ''
        elif element.text is not None:
            return element.text
        else:
            return ''
