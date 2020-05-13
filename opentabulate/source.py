# -*- coding: utf-8 -*-
"""
Source file API.

This module defines the Source class for OpenTabulate, which is an object that stores
metadata about the datasets to be processed by OpenTabulate. A "source file" written
in JSON will store this metadata and the Source object will read it during 
initialization. The metadata is extracted and validated using the parse() method.

Note: the Source object is not meant to be modified by external functions or classes.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import json
import logging
import os
import re
import sys
from ast import literal_eval

class Source(object):
    """
    Source class. Stores the metadata of a dataset pertaining to the file (format,
    filename, etc.) and structure (XML headers, CSV delimiter, schema, etc.). Other
    processing metadata inferred from a source file (e.g. file paths) used by 
    OpenTabulate are also stored.

    Attributes:
        src_path (str): Source file path.
        metadata (dict): Source file JSON dumps.
        p_args (argparse.Namespace) OpenTabulate (parsed) command line arguments.
        config (configparser.ConfigParser): OpenTabulate configuration file.

        default_paths (bool): For developers; set to False for unit test writing.
        
        local_file (str): Data file name (not path).
        input_path (str): Raw data path (in './data/input/').
        output_path (str): Tabulated data path (in './data/output/').

        column_map (dict): Mapping of input data schema to output schema. The output
            schema labels are defined by the user in a configuration file.

        logger (Logger): Logger with self.localfile as its name.
    """
    def __init__(self, path, p_args=None, config=None, default_paths=True):
        """
        Initializes a new source file object.

        Args:
            path (str): Path string to source file.
            p_args (argparse.Namespace): Parsed arguments.
            config (Configuration): OpenTabulate configuration file.
            default_paths (bool): For developers; set to False for unit test writing.

        Raises:
            OSError: Path (of source file) does not exist.
        """
        if not os.path.exists(path):
            raise OSError('Path "%s" does not exist.' % path)
        self.src_path = path
        try:
            with open(path) as f:
                self.metadata = json.load(f)
        except:
            raise # either raises JSONDecodeError or a file reading exception

        self.p_args = p_args
        self.config = config

        # 
        self.default_paths = default_paths
        
        # tabulation variables -- determined during parsing
        self.local_file = None
        self.input_path = None
        self.output_path = None

        self.column_map = None

        self.logger = None

        
    def parse(self):
        """
        Parses and validates most of the contents of a source file and stores the 
        metadata into the Source object.

        Validation primarily focuses on correct JSON typing, JSON key locations,
        key naming and inserting required key-value pairs. Regarding validation of
        key values, most of these are done by checking if they match hard-coded 
        values (e.g. character encoding or input file format). 

        Otherwise if there are any errors with the values, they will be likely be
        discovered during data processing. It is left to the responbility of the
        user that the target output matches the intension of the user.
        
        Note: validation is not done for existence of duplicate entries, empty 
            strings or paths of datasets.

        Raises:
            LookupError: Missing tag.
            SyntaxError: Incorrectly formatted group in configuration file.
            TypeError: Incorrect JSON type for a tag.
            ValueError: Incorrect entry (key or value) or combination or entries.
        """
        src_basename = os.path.basename(self.src_path)

        #####################
        # REQUIRED METADATA #
        #####################

        # first set of required tags
        required_tags = ('localfile', 'format', 'schema', 'schema_groups')
        for tag in required_tags:
            if tag not in self.metadata:
                raise LookupError("%s '%s' tag is missing." % (src_basename, tag))
            
        # types required for required tags
        if not isinstance(self.metadata['localfile'], str):
            raise TypeError("%s 'localfile' must be a string." % src_basename)
        if not isinstance(self.metadata['format'], dict):
            raise TypeError("%s 'format' must be an object." % src_basename)
        if not isinstance(self.metadata['schema'], dict):
            raise TypeError("%s 'schema' must be an object." % src_basename)
        
        # required schema groups as defined in the configuration file
        db_types = tuple([group for group in self.config['labels']])
        
        schema_groups = self.metadata['schema_groups']

        if isinstance(schema_groups, str):
            if schema_groups not in db_types:
                raise ValueError(
                    "%s schema group does not appear in '%s'" % (src_basename, schema_groups)
                )
            else:
                schema_groups = [schema_groups] # turn schema_groups into a list
                
        elif isinstance(schema_groups, list):
            for group in schema_groups:
                if group not in db_types:
                    raise ValueError(
                        "%s schema group does not appear in '%s'" % (src_basename, schema_groups)
                    )
            
        else:
            raise TypeError("%s 'schema_groups' must be a string or list." % src_basename)

        # required tags for 'format'
        if 'type' not in self.metadata['format']:
            raise LookupError("%s 'format.type' tag is missing." % src_basename)
        if not isinstance(self.metadata['format']['type'], str):
            raise TypeError("%s 'format.type' must be a string." % src_basename)

        # required formats
        if (self.metadata['format']['type'] == 'csv'):
            # -- CSV --
            # delimiter
            if 'delimiter' not in self.metadata['format']:
                raise LookupError("%s 'format.delimiter' tag is missing for format 'csv'" % src_basename)
            elif not (isinstance(self.metadata['format']['delimiter'], str) and
                      len(self.metadata['format']['delimiter']) == 1):
                raise TypeError("%s 'format.delimiter' must be a single character string." % src_basename)
            
            # quotes
            if 'quote' not in self.metadata['format']:
                raise LookupError("%s 'format.quote' tag is missing for format 'csv'" % src_basename)
            elif not (isinstance(self.metadata['format']['quote'], str) and
                      len(self.metadata['format']['quote']) == 1):
                raise TypeError("%s 'format.quote' must be a single character string." % src_basename)
            
        elif (self.metadata['format']['type'] == 'xml'):
            # -- XML --
            # xml header
            if 'header' not in self.metadata['format']:
                raise LookupError("%s 'format.header' tag is missing for format 'xml'" % src_basename)
            elif not isinstance(self.metadata['format']['header'], str):
                raise TypeError("%s 'format.header' must be a string." % src_basename)
        else:
            # -- unsupported format --
            raise ValueError("%s Unsupported data format '%s'" % (src_basename, self.metadata['format']['type']))
        
        #####################
        # OPTIONAL METADATA #
        #####################

        # dataset provider (name)
        if 'provider' in self.metadata and (not isinstance(self.metadata['provider'], str)):
            raise TypeError("%s 'provider' must be a string." % src_basename)

        # -- filter contents check --
        if 'filter' in self.metadata:
            if not isinstance(self.metadata['filter'], dict):
                raise TypeError("%s 'filter' must be an object." % src_basename)
            else:
                for attribute in self.metadata['filter']:
                    if not isinstance(self.metadata['filter'][attribute], str):
                        raise TypeError(
                            "%s Filter attribute '%s' must be a string (regex)." % (src_basename, attribute)
                        )
                    else:
                        attr_filter = self.metadata['filter'][attribute]
                        regexp = re.compile(attr_filter)
                        self.metadata['filter'][attribute] = regexp

        ###################
        # PATH ASSIGNMENT #
        ###################
        
        self.localfile = self.metadata['localfile']

        if self.default_paths:
            dirs = {
                'input' : './data/input',
                'output' : './data/output'
            }
            extensions = ('.csv', '.xml')
            basename = os.path.splitext(self.localfile)

            assert basename[1] in extensions, \
                "%s 'localfile' has an invalid file extension '%s'" % (src_basename, basename[1])
            
            self.input_path = os.path.join(dirs['input'], self.localfile)
            self.output_path = os.path.join(dirs['output'], basename[0] + '.csv')

        # check entire source to make sure correct keys are being used
        root_layer = ('localfile', 'format', 'schema_groups', 'encoding', 'schema',
                      'filter', 'provider', 'licence', 'source')
        format_layer = ('type', 'header', 'quote', 'delimiter')
        
        for i in self.metadata:
            if i not in root_layer:
                raise ValueError("%s Invalid key in root_layer '%s' in source file" % (src_basename, i))
            
        for i in self.metadata['format']:
            if i not in format_layer:
                raise ValueError("%s Invalid key in format_layer '%s' in source file" % (src_basename, i))

        #############################################
        # SCHEMA VALIDATION AND COLUMN NAME MAPPING #
        #############################################
        
        # check contents of 'schema' and build the column map (to be used for label map)
        column_names = tuple()

        for group in schema_groups:
            group_labels = literal_eval(self.config.get('labels', group))
            if not isinstance(group_labels, tuple):
                raise SyntaxError(
                    "%s Invalid config syntax for label in group %s" % (src_basename, group)
                )
            column_names += group_labels

        self.column_map = dict()

        def is_leaf(a):
            if isinstance(a, str):
                return True
            elif isinstance(a, list):
                for item in a:
                    if not isinstance(item, str):
                        return False
                return True
            else:
                return False
        
        for k in self.metadata['schema']:
            node = self.metadata['schema'][k]
            
            if is_leaf(node):
                if k not in column_names:
                    raise ValueError("%s: Invalid key '%s', must be target column name(s) if value"
                                     " is a string or list of strings." % (src_basename, k))

                self.column_map[k] = node

            elif isinstance(node, dict):
                if k not in schema_groups:
                    raise ValueError("%s: Invalid key '%s', must be a group label if value is an"
                                     " object." % (src_basename, k))

                # otherwise check that children are keys to a column name
                for c in node:
                    child = node[c]
                    if not is_leaf(child):
                        raise TypeError("%s: Value of key '%s' in group '%s' must be a string or list"
                                          " of strings." % (src_basename, c, k))

                    if c not in column_names:
                        raise ValueError("%s: Invalid key '%s' in group '%s', must be target column name(s)."
                                         % (src_basename, c, k))

                    self.column_map[c] = child
                    
            else:
                raise TypeError("%s: Value of key '%s' must be a string, list of strings, or object."
                                  % (src_basename, k))
            
        # set logger for source file
        self.logger = logging.getLogger(self.localfile)
