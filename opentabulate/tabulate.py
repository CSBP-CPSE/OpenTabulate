# -*- coding: utf-8 -*-
"""
Tabulation and processing API.

This module defines the core OpenTabulate API, which contains wrapper classes and 
methods for parsing, processing, and reformatting microdata to CSV format. The 
DataProcess class wraps the Algorithm class methods and its child classes to process 
specific data formats (currently CSV and XML format).


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
import logging
import operator
import os
import re
import subprocess
import sys
from xml.etree import ElementTree

from opentabulate.source import Source
from opentabulate.algorithm import *

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
        if self.source.metadata['format']['type'] == 'csv':
            fmt_algorithm = CSV_Algorithm(self.source,
                                          self.dp_address_parser)
            csv_encoding = fmt_algorithm.char_encode_check()
            self.source.metadata['encoding'] = csv_encoding # to prevent redundant brute force encoding checks
        elif self.source.metadata['format']['type'] == 'xml':
            fmt_algorithm = XML_Algorithm(self.source,
                                          self.dp_address_parser)
            #fmt_algorithm.remove_xmlns(self.source)
        # need the following line so the Algorithm wrapper methods work
        self.algorithm = fmt_algorithm
        
    def extractLabels(self):
        """
        Algorithm wrapper method. 

        Extracts data labels as indicated by a source file.
        """
        self.algorithm.extract_labels()

    def parse(self):
        """
        Algorithm wrapper method. 

        Parses and tabulates the source dataset based on label extraction.
        """
        self.algorithm.parse()

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
