# -*- coding: utf-8 -*-
"""
Unit tests for processing components (algorithm.py) of OpenTabulate.


Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

import re
import os
import sys
import unittest

try:
    from opentabulate.source import Source
    from opentabulate.algorithm import XML_Algorithm
    from opentabulate.algorithm import Algorithm
except ImportError:
    print("ERROR, could not import OpenTabulate API.", file=sys.stderr)
    exit(1)


def cmp_output_bytes(path1, path2):
    '''Compare the output of two files (specified by path).'''
    with open(path1, 'rb') as file1, open(path2, 'rb') as file2:

        while True:
            chunk1 = file1.read(4096)
            chunk2 = file2.read(4096)
            # if chunks differ, files are not the same
            if (chunk1 != chunk2):
                return False
            # otherwise, check if we have reached EOF
            if (chunk1 == b'' or chunk2 == b''):
                break
        return True


class TestAlgorithmProcess(unittest.TestCase):
    """
    Algorithm class unit tests to verify correct output after running extract_labels() 
    and parse() methods.
    """
    @classmethod
    def setUpClass(cls):
        cls.src_input = "xml-source.json"
        cls.target_output = "xml-target-output.csv"
        cls.test_output = "xml-test-output.csv"
        cls.a = Algorithm()

    def test_basic_process_csv(self):
        """
        OpenTabulate CSV parsing and tabulation test.
        """
        pass # TO DO..
      
    def test_basic_process_xml(self):
        """
        OpenTabulate XML parsing and tabulation test.
        """
        source = Source(self.src_input, default_paths=False)
        source.parse()
        source.rawpath = source.localfile
        source.dirtypath = self.test_output
        
        xml_alg = XML_Algorithm(source)
        xml_alg.extract_labels()
        xml_alg.parse()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.test_output)
        )
    #
    #  work here -- 2020 March 12 --
    #
    def test___generate_field_names(self):
        """
        Test for Algorithm._generateFieldNames method. The method generates
        headers (column names) for CSV files. 

        If the address parse keyword 'address_parse_str' is missing, 
        the output headers should be exactly the same as the input keys
        Otherwise, address tokens should be inserted into the header in 
        place of where the keyword appeared.
        """
        # 'address_parse_str' is absent
        keys_without_parse = ['name']
        self.assertEqual(
            self.a._generateFieldNames(keys_without_parse), keys_without_parse
        )

        # 'address_parse_str' appears in the first index
        keys_parse_left = ['address_str_parse', 'name']
        target_left = [i for i in self.a.ADDR_FIELD_LABEL] + ['name']
        self.assertEqual(
            self.a._generateFieldNames(keys_parse_left), target_left
        )

        # 'address_parse_str' appears in the last index
        keys_parse_right = ['name', 'address_str_parse']
        target_right = ['name'] + [i for i in self.a.ADDR_FIELD_LABEL]
        self.assertEqual(
            self.a._generateFieldNames(keys_parse_right), target_right
        )
        
    def test___is_row_empty(self):
        """
        Test for self.a._isRowEmpty method.

        A row contains all empty strings iff the method returns True.
        """
        
        self.assertTrue(self.a._isRowEmpty({0 : '', 1 : '', 2 : ''}))
        self.assertTrue(self.a._isRowEmpty(dict()))
        self.assertFalse(self.a._isRowEmpty({0 : '', 1 : 'test'}))
        self.assertFalse(self.a._isRowEmpty({0 : 'test', 1 : ''}))

    def test___quick_scrub(self):
        """
        Test for self.a._quickScrub method.

        This method does basic cleaning to the input string. It should:
          - remove redundant whitespace
          - lowercase the output
        """
        self.assertEqual(self.a._quickScrub(''), '')
        self.assertEqual(self.a._quickScrub('\t\n '), '')
        self.assertEqual(self.a._quickScrub(' E '), 'e')
        self.assertEqual(self.a._quickScrub('E '), 'e')
        self.assertEqual(self.a._quickScrub(' E'), 'e')
        self.assertEqual(self.a._quickScrub('\na\tb\t'), 'a b')

    def test___clean(self): # ! original function subject to change
        pass
    #
    # end here -- 2020 March 12 --
    #

    @classmethod
    def tearDownClass(cls):
        pass
        #os.remove(cls.test_output)

if __name__ == '__main__':
    unittest.main()
