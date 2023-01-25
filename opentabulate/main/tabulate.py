# -*- coding: utf-8 -*-
"""
This module provides the DataProcess class, which wraps the methods from the (child)
Algorithm classes to define the data processing pipeline. It is meant to be used by
the OpenTabulate command-line script (or any script that the command-line one 
references) to define the data processing pipeline in a compact and readable way.

The Algorithm classes are designed to process and tabulate a CSV or XML file to 
OpenTabulate's defined CSV format.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

import csv
import logging
import operator
import os
import re
import subprocess
import sys
from xml.etree import ElementTree

from opentabulate.main.source import Source
from opentabulate.main.algorithms import *

class DataProcess(object):
    """
    A data processing interface for a source file. 
    
    Attributes:
        source (Source): Dataset abstraction.
    """
    def __init__(self, source=None, algorithm=None):
        """
        Initialize a DataProcess object.

        Args:
            source (Source): Dataset abstraction.
            algorithm (Algorithm): Any (sub)class of Algorithm.
        """
        self.source = source
        self.algorithm = algorithm

    def prepareData(self, interrupt=None):
        """
        Algorithm wrapper function.

        Selects a Algorithm subclass to be used to process data referred to by 
        the source file.

        Args:
            interrupt (threading.Event): Event to halt multi-threaded processing.

        Raises:
            Data format unknown.
        """
        format = self.source.metadata['format']['type'] 
        if format == 'csv':
            fmt_algorithm = CSV_Algorithm(self.source, interrupt)
            if 'encoding' not in self.source.metadata:
                csv_encoding = fmt_algorithm.char_encode_check()
                self.source.metadata['encoding'] = csv_encoding # prevents redundant encoding checks
        elif format == 'xml':
            fmt_algorithm = XML_Algorithm(self.source, interrupt)
        elif format == 'geojson':
            fmt_algorithm = GeoJSON_Algorithm(self.source, interrupt)
        elif format == 'json':
            fmt_algorithm = JSON_Algorithm(self.source, interrupt)
        else:
            raise ValueError("Data format %s unknown." % format)
            
        # initialize self.algorithm for other methods
        self.algorithm = fmt_algorithm
        
    def constructLabelMap(self):
        """
        Algorithm wrapper function..

        Constructs mapping of input data labels to output data labels.
        """
        self.algorithm.construct_label_map()

    def tabulate(self):
        """
        Algorithm wrapper function. 

        Parses and tabulates the source dataset based on label map.
        """
        self.algorithm.tabulate()
