# -*- coding: utf-8 -*-
"""
XML_Algorithm.

Algorithm class. The XML_Algorithm class provides methods for parsing, 
processing and tabulating XML input data into CSV format.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

#######################
# MODULES AND IMPORTS #
#######################

import csv
from xml.etree import ElementTree

from .algorithm import Algorithm
from opentabulate.main.thread_exception import ThreadInterruptError

#####################################
# DATA PROCESSING ALGORITHM CLASSES #
#####################################
        
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

        with self._openOutputFile() as csvfile:
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
        # Note: tag_name and head_element were originally intended for logging and
        # might be used this way in the future. It's current use is for debugging!
        if element is None:
            return ''
        elif element.text is not None:
            return element.text
        else:
            return ''
