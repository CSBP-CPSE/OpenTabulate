# -*- coding: utf-8 -*-
"""
Tabulation API.

This module defines the core functionality of OpenTabulate, which contains the 
Algorithm class. The classes provide methods for parsing, 
processing and tabulating input data into CSV format.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

#######################
# MODULES AND IMPORTS #
#######################

import platform
import re
from abc import ABC, abstractmethod

from opentabulate.main.config import SUPPORTED_ENCODINGS
from opentabulate.main.thread_exception import ThreadInterruptError

#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class Algorithm(ABC):
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

    @abstractmethod
    def tabulate(self):
        """Mandatory method for all subclasses"""

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

        self.platform = platform.system()

        self.FORCE_REGEXP = re.compile('force:.*')

        # flags
        self.OUTPUT_ENC_ERRORS = None
        self.FILTER_FLAG = None
        self.PROVIDER_FLAG = None
        self.ADD_INDEX = None
        self.NO_WHITESPACE = None
        self.LOWERCASE = None
        self.TITLECASE = None
        self.UPPERCASE = None

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
                # titlecase has lower priority than lowercase
                self.TITLECASE = (not self.LOWERCASE) and source.config.getboolean('general', 'titlecase_output')
                # uppercase has the lowest priority
                self.UPPERCASE = (not (self.LOWERCASE or self.TITLECASE)) and source.config.getboolean('general', 'uppercase_output')

            source.logger.debug("FILTER_FLAG set to %s" % self.FILTER_FLAG)
            source.logger.debug("PROVIDER_FLAG set to %s" % self.PROVIDER_FLAG)
            source.logger.debug("ADD_INDEX set to %s" % self.ADD_INDEX)
            source.logger.debug("NO_WHITESPACE set to %s" % self.NO_WHITESPACE)
            source.logger.debug("LOWERCASE set to %s" % self.LOWERCASE)
            source.logger.debug("TITLECASE set to %s" % self.TITLECASE)
            source.logger.debug("UPPERCASE set to %s" % self.UPPERCASE)
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
        elif self.TITLECASE: # make entries titlecase
            entry = entry.title()
        elif self.UPPERCASE: # make entries uppercase
            entry = entry.upper()


        return entry

    def _isForceValue(self, value):
        """Returns True if value contains the prefix 'force:'."""
        return bool(self.FORCE_REGEXP.match(value))

    def _openInputFile(self):
        """Open input file"""
        return open(self.source.input_path, 'r', encoding=self.char_encode_check())

    def _openOutputFile(self):
        """Platform-specific file open, avoids empty CSV lines on Windows"""

        # on Windows, remove extra newline
        # https://docs.python.org/3/library/csv.html#examples
        if self.platform == "Windows":
            newl = ''
        else:
            newl = '\n'

        return open(self.source.output_path, 'w',
                  encoding=self.source.config.get('general', 'target_encoding'),
                  errors=self.OUTPUT_ENC_ERRORS,
                  newline=newl) 