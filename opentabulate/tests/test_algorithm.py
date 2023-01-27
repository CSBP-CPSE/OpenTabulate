# -*- coding: utf-8 -*-
"""
Unit tests for processing components (algorithm.py) of OpenTabulate.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

import re
import os
import unittest
from xml.etree.ElementTree import Element as xmlElement

from opentabulate.main.source import Source
from opentabulate.main.config import Configuration
from opentabulate.main.algorithms import Algorithm, CSV_Algorithm, XML_Algorithm, GeoJSON_Algorithm, JSON_Algorithm


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


# Mock class for testing Algorithm
# Implements empty tabulate
class MockAlgorithm(Algorithm):
    def tabulate(self):
        pass

class TestAlgorithm(unittest.TestCase):
    """
    Algorithm class unit tests to verify correct output after running extract_labels() 
    and parse() methods.
    """
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'data')

        cls.config_file = data_path + "/opentabulate.conf"

        # GeoJSON files for testing
        cls.geojson_src_input = data_path + "/geojson-source.json"
        cls.geojson_test_input = data_path + "/geojson-data.geojson"
        cls.geojson_target_output = data_path + "/geojson-target-output.csv"
        cls.geojson_test_output = data_path + "/geojson-test-output.csv"

        # XML files for testing
        cls.xml_src_input = data_path + "/xml-source.json"
        cls.xml_test_input = data_path + "/xml-data.xml"
        cls.xml_target_output = data_path + "/xml-target-output.csv"
        cls.xml_test_output = data_path + "/xml-test-output.csv"

        # CSV files for testing
        cls.csv_src_input = data_path + "/csv-source.json"
        cls.csv_test_input = data_path + "/csv-data.csv"
        cls.csv_target_output = data_path + "/csv-target-output.csv"
        cls.csv_test_output = data_path + "/csv-test-output.csv"
        
        cls.a  = MockAlgorithm()
        cls.xa = XML_Algorithm()

    def test_basic_process_csv(self):
        """
        OpenTabulate CSV parsing and tabulation test.
        """
        config = Configuration(self.config_file)
        config.load()
        config.validate()

        source = Source(self.csv_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.csv_test_input
        source.output_path = self.csv_test_output

        csv_alg = CSV_Algorithm(source)
        csv_alg.construct_label_map()
        csv_alg.tabulate()

        self.assertTrue(
            cmp_output_bytes(self.csv_target_output, self.csv_test_output)
        )
      
    def test_basic_process_xml(self):
        """
        OpenTabulate XML parsing and tabulation test.
        """
        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.xml_src_input, config=config, default_paths=False)
        source.parse()
        
        source.input_path = self.xml_test_input
        source.output_path = self.xml_test_output
        
        xml_alg = XML_Algorithm(source)
        xml_alg.construct_label_map()
        xml_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.xml_target_output, self.xml_test_output)
        )

    def test_basic_process_geojson(self):
        """
        OpenTabulate GeoJSON parsing and tabulation test.
        """
        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.geojson_src_input, config=config, default_paths=False)
        source.parse()
        
        source.input_path = self.geojson_test_input
        source.output_path = self.geojson_test_output
        
        geojson_alg = GeoJSON_Algorithm(source)
        geojson_alg.construct_label_map()
        geojson_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.geojson_target_output, self.geojson_test_output)
        )

    def test__is_row_empty(self):
        """
        Test for Algorithm._isRowEmpty method.

        A row contains all empty strings iff the method returns True.
        """
        self.assertTrue(self.a._isRowEmpty({0 : '', 1 : '', 2 : ''}))
        self.assertTrue(self.a._isRowEmpty(dict()))
        self.assertFalse(self.a._isRowEmpty({0 : '', 1 : 'test'}))
        self.assertFalse(self.a._isRowEmpty({0 : 'test', 1 : ''}))

    def test__quick_clean_entry(self):
        """
        Test for Algorithm._quickCleanEntry method.

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

        self.a.TITLECASE = True

        self.assertEqual(self.a._quickCleanEntry('ABCabc123!@$'), 'Abcabc123!@$')

        self.a.TITLECASE = None

        self.a.UPPERCASE = True

        self.assertEqual(self.a._quickCleanEntry('ABCabc123!@$'), 'ABCABC123!@$')

        self.a.UPPERCASE = None

    def test__is_force_value(self):
        """
        Test for Algorithm._isForceValue method.

        Checks if a string matches the regular expression '^force:.*'.
        """
        self.assertTrue(self.a._isForceValue('force:'))
        self.assertTrue(self.a._isForceValue('force:a'))
        self.assertFalse(self.a._isForceValue('Force:a'))
        self.assertFalse(self.a._isForceValue('FORCE:a'))
        self.assertFalse(self.a._isForceValue('force a'))
        self.assertFalse(self.a._isForceValue('force'))

    def test__xml_is_element_missing(self):
        """
        Test for XML_Algorithm._is_xml_element_missing method.
        
        Identifies if a XML element object has missing components, which should
        return empty strings instead of None values.
        """
        element = xmlElement('tag')

        self.assertEqual(self.xa._xml_is_element_missing(None, None, None), '')
        self.assertEqual(self.xa._xml_is_element_missing(element, None, None), '')

        text = 'hello world'
        element.text = text

        self.assertEqual(self.xa._xml_is_element_missing(element, None, None), text)
        
    @classmethod
    def tearDownClass(cls):
        pass

class TestJSON_Algorithm(unittest.TestCase):
    """
    Algorithm class unit tests to verify correct output after running extract_labels() 
    and parse() methods.
    """
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), 'data')

        cls.config_file = data_path + "/opentabulate.conf"
        cls.target_output = data_path + "/json-target-output.csv"

        # JSON files - split format
        cls.split_src_input = data_path + "/json-split-source.json"
        cls.split_test_input = data_path + "/json-split-data.json"
        cls.split_test_output = data_path + "/json-split-test-output.csv"

        # JSON files - records format
        cls.records_src_input = data_path + "/json-records-source.json"
        cls.records_test_input = data_path + "/json-records-data.json"
        cls.records_test_output = data_path + "/json-records-test-output.csv"

        # JSON files - index format
        cls.index_src_input = data_path + "/json-index-source.json"
        cls.index_test_input = data_path + "/json-index-data.json"
        cls.index_test_output = data_path + "/json-index-test-output.csv"

        # JSON files - columns format
        cls.columns_src_input = data_path + "/json-columns-source.json"
        cls.columns_test_input = data_path + "/json-columns-data.json"
        cls.columns_test_output = data_path + "/json-columns-test-output.csv"

        # JSON files - table format
        cls.table_src_input = data_path + "/json-table-source.json"
        cls.table_test_input = data_path + "/json-table-data.json"
        cls.table_test_output = data_path + "/json-table-test-output.csv"

    def test_basic_process_split_data(self):
        """
        OpenTabulate JSON parsing and tabulation test - split data format
        """

        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.split_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.split_test_input
        source.output_path = self.split_test_output
        
        json_alg = JSON_Algorithm(source)
        json_alg.construct_label_map()
        json_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.split_test_output)
        )

    def test_basic_process_records_data(self):
        """
        OpenTabulate JSON parsing and tabulation test - records data format
        """

        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.records_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.records_test_input
        source.output_path = self.records_test_output
        
        json_alg = JSON_Algorithm(source)
        json_alg.construct_label_map()
        json_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.records_test_output)
        )

    def test_basic_process_index_data(self):
        """
        OpenTabulate JSON parsing and tabulation test - index data format
        """

        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.index_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.index_test_input
        source.output_path = self.index_test_output
        
        json_alg = JSON_Algorithm(source)
        json_alg.construct_label_map()
        json_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.index_test_output)
        )

    def test_basic_process_columns_data(self):
        """
        OpenTabulate JSON parsing and tabulation test - columns data format
        """

        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.columns_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.columns_test_input
        source.output_path = self.columns_test_output
        
        json_alg = JSON_Algorithm(source)
        json_alg.construct_label_map()
        json_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.columns_test_output)
        )

    def test_basic_process_table_data(self):
        """
        OpenTabulate JSON parsing and tabulation test - table data format
        """

        config = Configuration(self.config_file)
        config.load()
        config.validate()
        
        source = Source(self.table_src_input, config=config, default_paths=False)
        source.parse()

        source.input_path = self.table_test_input
        source.output_path = self.table_test_output
        
        json_alg = JSON_Algorithm(source)
        json_alg.construct_label_map()
        json_alg.tabulate()
        
        self.assertTrue(
            cmp_output_bytes(self.target_output, self.table_test_output)
        )

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
