# -*- coding: utf-8 -*-
"""
OpenTabulate configuration file parser and class.

This reads '$HOME/.config/opentabulate.conf' using the ConfigParser class and 
configures the OpenTabulate command line tool. It stores information such as where 
the OpenTabulate root directory is, tabulation parameters (e.g. output encoding,
indexing, specific output formatting) and the available target output columns listed 
in groups. The command line arguments take higher priority over the configuration
file unless stated otherwise.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import os
import sys
from configparser import ConfigParser
from ast import literal_eval

DEFAULT_PATHS = {'conf_dir' : os.path.expanduser('~') + '/.config',
                 'conf_file' :os.path.expanduser('~') + '/.config/opentabulate.conf'}

SUPPORTED_ENCODINGS = ('utf-8', 'cp1252')
ENCODING_ERRORS = ('strict', 'replace', 'ignore')

class ConfigError(Exception):
    """
    Configuration exception class. Primarily to be used for configuration file
    validation errors.
    """

class Configuration(ConfigParser):
    """
    Child class of the built-in module ConfigParser. Adapted to read a hard-coded
    location for a configuration file upon initialization and to validate its
    contents.

    Attributes:
        conf_path (str): Configuration file path.
    """
    def __init__(self, conf_path=None):
        """
        Initializes ConfigParser object with configuration path. If the path is set
        to None, use the default path.
        """
        super().__init__(strict=True, empty_lines_in_values=False)

        if conf_path is None:
            self.conf_path = DEFAULT_PATHS['conf_file']
        else:
            self.conf_path = conf_path

    def load(self):
        """
        Load the configuration file.

        Raises:
            FileNotFoundError: configuration file is missing from path
        """
        if not os.path.exists(self.conf_path):
            raise FileNotFoundError("No configuration file found in %s" % self.conf_path)
        else:
            try:
                self.read(self.conf_path)
            except:
                raise
        
    def validate(self):
        """
        Validates the contents of the configuration file.

        Note: Existence of the OpenTabulate root directory and its folder contents are 
            not validated. This is handled separately by the command line argument
            handler due to how the --initialize flag is handled.

        Raises:
            ConfigError: Validation error of loaded configuration
        """
        base_sections = ('general', 'labels')
    
        general_section = ('root_directory', 'add_index', 'target_encoding',
                           'output_encoding_errors', 'clean_whitespace', 
                           'lowercase_output', 'titlecase_output', 'uppercase_output',
                           'log_level')

        reserved_cols = ('idx', 'provider')
        
        # check that the mandatory section 'general' and option 'root_directory' are present
        # in the configuration file
        try:
            assert 'general' in self.sections()
        except AssertionError:
            raise ConfigError("Missing 'general' section")

        try:
            assert 'root_directory' in self['general']
        except AssertionError:
            raise ConfigError("Missing required 'root_directory' option in 'general' section")

        # check if configuration sections are valid
        for sec in self.sections():
            if sec not in base_sections:
                raise ConfigError("'%s' is not a valid section" % sec)

        # check if 'general' section has invalid options
        for option in self['general']:
            if option not in general_section:
                raise ConfigError("'%s' is not a valid option in 'general' section" % option)

        # check if 'labels' section is using core labels
        for option in self['labels']:
            if option in general_section:
                raise ConfigError("Cannot define label '%s', is a reserved word" % option)

        # add default settings then validate
        defaults = {'target_encoding' : 'utf-8',
                    'output_encoding_errors' : 'strict',
                    'add_index' : 'false',
                    'clean_whitespace' : 'false',
                    'lowercase_output' : 'false',
                    'titlecase_output' : 'false',
                    'uppercase_output' : 'false',
                    'log_level' : '3'}

        for def_opt in defaults:
            if def_opt not in self['general']:
                self.set('general', def_opt, defaults[def_opt])

        # validate boolean options
        boolean_options = ('add_index', 'clean_whitespace', 'lowercase_output', 'titlecase_output', 'uppercase_output')
        for option in boolean_options:
            try:
                self.getboolean('general', option)
            except ValueError:
                raise ConfigError("Option '%s' in 'general' section is not a"
                                  " boolean value" % option)

        # validate verbosity level
        try:
            log_level = self.getint('general', 'log_level')
            assert log_level >= 0 and log_level <= 3
        except:
            raise ConfigError("Option '%s' in 'general' is not an integer value"
                              " between 0 and 3 (inclusive)" % option)

        # validate encoding
        encoding = self.get('general', 'target_encoding')
        if encoding not in SUPPORTED_ENCODINGS:
            raise ConfigError("'%s' is not a supported output encoding" % encoding)

        # validate output encoding error handling
        handler = self.get('general', 'output_encoding_errors')
        if handler not in ENCODING_ERRORS:
            raise ConfigError("'%s' is not an output encoding error handler" % handler) 

        # validate labels to make sure they are tuples and column names are not
        # reserved words
        for option in self['labels']:
            value = None

            try:
                value = literal_eval(self.get('labels', option))
                assert isinstance(value, tuple)
            except:
                raise ConfigError("Value of label '%s' is not a tuple" % option)

            for col in value:
                if col in reserved_cols:
                    raise ConfigError("Column name '%s' cannot be used, is a reserved"
                                      " word" % col)
