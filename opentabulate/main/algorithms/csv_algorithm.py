# -*- coding: utf-8 -*-
"""
CSV_Algorithm.

Algorithm class. The CSV_Algorithm class provides methods for parsing, 
processing and tabulating CSV input data into CSV format.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

#######################
# MODULES AND IMPORTS #
#######################

import csv
import re

from .algorithm import Algorithm
from opentabulate.main.thread_exception import ThreadInterruptError

#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
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

        with self._openInputFile() as csv_file_read, \
            self._openOutputFile() as csv_file_write:
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
