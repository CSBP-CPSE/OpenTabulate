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

SUPPORTED_ENCODINGS = ('utf-8', 'cp1252')

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
        Initializes ConfigParser object and attempts to read hard-coded configuration
        file.
        """
        super().__init__(strict=True, empty_lines_in_values=False)

        if conf_path is None:
            conf_dir = os.path.expanduser('~') + '/.config'
            self.conf_path = conf_dir + '/opentabulate.conf'
        else:
            self.conf_path = conf_path
            

        if not os.path.exists(self.conf_path):
            print("No configuration file found in %s." % conf_path, file=sys.stderr)
            sys.exit(1)
        else:
            try:
                self.read(self.conf_path)
            except Exception as e:
                print(e)
                print("Failed to read configuration file, exiting.", file=sys.stderr)
                sys.exit(1)

    def validate(self):
        """
        Validates the contents of the configuration file.

        Note: Existence of the OpenTabulate root directory and its folder contents are 
            not validated. This is handled separately by the command line argument
            handler due to how the --initialize flag is handled.
        """
        base_sections = ('general', 'labels')
    
        general_section = ('root_directory', 'add_index', 'target_encoding',
                           'clean_whitespace', 'lowercase_output', 'log_level')

        reserved_words = general_section + ('idx', 'provider')
        
        # check that the mandatory section 'general' and option 'root_directory' are present
        # in the configuration file
        try:
            assert 'general' in self.sections()
        except AssertionError:
            print("Configuration error: missing 'general' section", file=sys.stderr)
            sys.exit(1)

        try:
            assert 'root_directory' in self['general']
        except AssertionError:
            print("Configuration error: missing required 'root_directory' option"
                  " in 'general' section", file=sys.stderr)
            sys.exit(1)

        # check that root directory is an absolute path
        try:
            assert os.path.isabs(
                os.path.expanduser(self.get('general', 'root_directory'))
            )
        except AssertionError:
            print("Configuration error: root directory must be an absolute path",
                  file=sys.stderr)
            sys.exit(1)
                
        # check if configuration sections are valid
        for sec in self.sections():
            if sec not in base_sections:
                print("Configuration error: section '%s' is not a valid section"
                      % section, file=sys.stderr)
                sys.exit(1)

        # check if 'general' section has invalid options
        for option in self['general']:
            if option not in general_section:
                print("Configuration error: option '%s' is not a valid option in"
                      " general section" % option, file=sys.stderr)
                sys.exit(1)

        # check if 'labels' section is using core labels
        for option in self['labels']:
            if option in reserved_words:
                print("Configuration error: cannot define label '%s', it is a"
                      " reserved word" % option, file=sys.stderr)
                sys.exit(1)

        # add default settings then validate
        defaults = {'add_index' : 'true',
                    'target_encoding' : 'utf-8',
                    'clean_whitespace' : 'false',
                    'lowercase_output' : 'false',
                    'log_level' : '3'}

        for def_opt in defaults:
            if def_opt not in self['general']:
                self.set('general', def_opt, defaults[def_opt])

        # validate boolean options
        boolean_options = ('add_index', 'clean_whitespace', 'lowercase_output')
        for option in boolean_options:
            try:
                self.getboolean('general', option)
            except ValueError:
                print("Configuration error: option '%s' in 'general' is not a boolean value"
                      % option, file=sys.stderr)
                sys.exit(1)

        # validate verbosity level
        try:
            log_level = self.getint('general', 'log_level')
            assert log_level >= 0 and log_level <= 3
        except:
            print("Configuration error: option '%s' in 'general' is not an integer value"
                  " between 0 and 3 (inclusive)" % option, file=sys.stderr)
            sys.exit(1)

        # validate encoding
        encoding = self.get('general', 'target_encoding')
        if encoding not in SUPPORTED_ENCODINGS:
            print("Configuration error: '%s' is not a supported target encoding"
                  % encoding, file=sys.stderr)
            sys.exit(1)

        # validate labels to make sure they are tuples
        for option in self['labels']:
            try:
                value = literal_eval(self.get('labels', option))
                assert isinstance(value, tuple)
            except:
                print("Configuration error: value of label '%s' is not a tuple"
                      % option, file=sys.stderr)
                sys.exit(1)
