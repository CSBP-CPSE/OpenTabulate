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
    from opentabulate.config import Configuration
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


class TestAlgorithm(unittest.TestCase):
    """
    Algorithm class unit tests to verify correct output after running extract_labels() 
    and parse() methods.
    """
    @classmethod
    def setUpClass(cls):
        cls.src_input = "xml-source.json"
        cls.target_output = "xml-target-output.csv"
        cls.test_output = "xml-test-output.csv"
        cls.config_file = "opentabulate.conf"
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
        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.src_input, config=config, default_paths=False)
        source.parse()
        
        source.input_path = source.localfile
        source.output_path = self.test_output
        
        xml_alg = XML_Algorithm(source)
        xml_alg.construct_label_map()
        xml_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.test_output)
        )
        
    def test__is_row_empty(self):
        """
        Test for self.a._isRowEmpty method.

        A row contains all empty strings iff the method returns True.
        """
        self.assertTrue(self.a._isRowEmpty({0 : '', 1 : '', 2 : ''}))
        self.assertTrue(self.a._isRowEmpty(dict()))
        self.assertFalse(self.a._isRowEmpty({0 : '', 1 : 'test'}))
        self.assertFalse(self.a._isRowEmpty({0 : 'test', 1 : ''}))

    def test__quick_clean_entry(self):
        """
        Test for self.a._quickCleanEntry method.

        This method does basic cleaning to the input string. It has the
        option to
          - remove redundant whitespace
          - lowercase the output
        Any implementation of the cleaning here must have it so that the
        options are done independently.
        """
        self.a.NO_WHITESPACE = True
        
        self.assertEqual(self.a._quickCleanEntry(''), '')
        self.assertEqual(self.a._quickCleanEntry('\t\n '), '')
        self.assertEqual(self.a._quickCleanEntry(' E '), 'E')
        self.assertEqual(self.a._quickCleanEntry('E '), 'E')
        self.assertEqual(self.a._quickCleanEntry(' E'), 'E')
        self.assertEqual(self.a._quickCleanEntry('\na\tb\t'), 'a b')

        self.a.NO_WHITESPACE = None

        self.a.LOWERCASE = True

        self.assertEqual(self.a._quickCleanEntry('ABCabc123!@$'), 'abcabc123!@$')

        self.a.LOWERCASE = None

    def test__is_force_value(self):
        self.assertTrue(self.a._isForceValue('force:'))
        self.assertTrue(self.a._isForceValue('force:a'))
        self.assertFalse(self.a._isForceValue('Force:a'))
        self.assertFalse(self.a._isForceValue('FORCE:a'))
        self.assertFalse(self.a._isForceValue('force a'))
        self.assertFalse(self.a._isForceValue('force'))
        
    @classmethod
    def tearDownClass(cls):
        pass
        #os.remove(cls.test_output)

if __name__ == '__main__':
    unittest.main()
