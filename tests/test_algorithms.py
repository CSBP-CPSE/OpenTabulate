# -*- coding: utf-8 -*-
"""
Unit tests for processing components of the OpenTabulate API.

...

Created and written by Maksym Neyra-Nesterenko.

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""
import os
import sys
import unittest

try:
    from opentabulate.source import Source
    from opentabulate.algorithm import XML_Algorithm
except ImportError:
    print("ERROR, could not import OpenTabulate API.", file=sys.stderr)
    exit(1)


def cmp_output_bytes(path1, path2):
    """
    Compare the output of two files (specified by path).
    """
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
        
        xml_alg = XML_Algorithm(database_type="business")
        xml_alg.extract_labels(source)
        xml_alg.parse(source)
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.test_output)
        )

    @classmethod
    def tearDownClass(cls):
        pass
        #os.remove(cls.test_output)

if __name__ == '__main__':
    unittest.main()
