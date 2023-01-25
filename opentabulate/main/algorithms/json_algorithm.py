# -*- coding: utf-8 -*-
"""
JSON_Algorithm.

Algorithm class. The JSON_Algorithm class provides methods for parsing, 
processing and tabulating JSON input data into CSV format.

Created and written by Marcello Barisonzi, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

#######################
# MODULES AND IMPORTS #
#######################

import csv
import os
import re
import pandas as pd

from .algorithm import Algorithm
from opentabulate.main.config import SUPPORTED_ENCODINGS
from opentabulate.main.thread_exception import ThreadInterruptError

#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
class JSON_Algorithm(Algorithm):
    """
    Algorithm child class designed to handle JSON formatted data.
    """

    def construct_label_map(self):
        """
        Constructs a dictionary from a column map that the 'tabulate' function uses to
        to reformat input data.
        """
        self.label_map = self.source.column_map

    def tabulate(self):
        """
        Parses a dataset in JSON format to transform into a standardized CSV format.

        Exceptions raised must be handled external to this module.

        Raises:
            ValueError: Label map for parsing data is missing.
        """
        
        if not hasattr(self, 'label_map'):
            raise ValueError("Missing 'label_map' for parsing, 'construct_label_map' was not ran")

        tags = dict([(v,k) for k,v in self.label_map.items()])

        orient = self.source.metadata['format']['orient']
        enc = self.char_encode_check()

        # read input file into DataFrame
        with open(self.source.input_path, 'r', encoding=enc) as f:
            df = pd.read_json(f, 'r', encoding=enc, orient=orient)

            df.rename(columns=tags, inplace=True)

            # drop columns not in tags:
            drop_columns = [i for i in df.columns if i not in self.label_map.keys()]
            df.drop(columns=drop_columns, inplace=True)

            if self.ADD_INDEX:
                df.reset_index(inplace=True, names="idx")

            if self.PROVIDER_FLAG:
                df['provider'] = self.source.metadata['provider']

            with self._openOutputFile() as o_f:
                df.to_csv(o_f, index=False)

        # TODO: UPPER/LOWER/TITLECASE, FORCE