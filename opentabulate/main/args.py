# -*- coding: utf-8 -*-
"""
Command line argument parser and handler for the OpenTabulate console script.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import os
import sys
import argparse
import logging
from opentabulate.main.config import ConfigError
from opentabulate.main.config import DEFAULT_PATHS as def_paths
from opentabulate.main.config import SUPPORTED_ENCODINGS as supp_enc
from opentabulate.main.config import ENCODING_ERRORS as enc_errs

def parse_arguments():
    """
    Define the command line argument structure and parse it.
    """
    cmd_args = argparse.ArgumentParser(
        description='OpenTabulate: a command-line data tabulation tool.',
        usage='%(prog)s [options] [SOURCE [SOURCE ...]]',
        add_help=False
    )
    # positional arguments
    positional_args = cmd_args.add_argument_group('positional arguments')
    positional_args.add_argument('SOURCE', nargs='*', default=None, help='path to source file')

    # runtime options
    runtime_args = cmd_args.add_argument_group('runtime arguments')
    runtime_args.add_argument('-h', '--help', action='help',
                              help='show this help message and exit')
    runtime_args.add_argument('--initialize', action='store_true', 
                              help='create processing directories')
    runtime_args.add_argument('-c', '--copy-config', action='store_true',
                              help='copy example config file to ~/.config/opentabulate')
    runtime_args.add_argument('-s', '--verify-source', action='store_true', default=False,
                              help='validate source files without processing data')
    runtime_args.add_argument('--clear-cache', action='store_true',
                              help='clear processing redundancy cache')
    runtime_args.add_argument('--ignore-cache', action='store_true',
                              help='ignore processing redundancy cache')
    runtime_args.add_argument('-t', '--threads', action='store', default=1, type=int, metavar='N',
                              help='multithread data processing on N threads')
    
    # configuration options
    config_args = cmd_args.add_argument_group('configuration arguments',
                                description='override configuration file options')
    config_args.add_argument('--add-index', action='store', default=None, type=str, metavar='BOOL',
                             help='insert index column to output')
    config_args.add_argument('--target-enc', action='store', default=None, type=str, metavar='ENCODING',
                             help='output character encoding')
    config_args.add_argument('--output-enc-errors', action='store', default=None, type=str, metavar='HANDLER',
                             help='error handler for character re-encoding')
    config_args.add_argument('--clean-ws', action='store', default=None, type=str, metavar='BOOL',
                             help='clean whitespace in output')
    config_args.add_argument('--lowercase', action='store', default=None, type=str, metavar='BOOL',
                             help='convert output to lowercase')
    config_args.add_argument('-l', '--log-level', action='store', default=None, type=int, metavar='N',
                             help='specify data processing log verbosity')
    
    return cmd_args.parse_args()


def validate_args_and_config(p_args, config, cache_mgrs):
    """
    Validate the configuration file and command line arguments, then perform
    actions based on the read parameters.

    Note:
        p_args is modified in this method.

    Args:
        p_args (argparse.Namespace): Parsed arguments.
        config (Configuration): OpenTabulate configuration.
        cache_mgrs (list): List of CacheManager objects.
    """
    data_folders = ('./data', './data/input', './data/output', './sources')
    
    if p_args.copy_config == True:
        if os.path.exists(def_paths['conf_file']):
            print("Configuration file already exists, not doing anything.", file=sys.stderr)
            sys.exit(1)
        
        conf_example = os.path.join(
            os.path.dirname(__file__),
            '../share/opentabulate.conf.example'
        )
        try:
            assert os.path.exists(conf_example)
        except AssertionError:
            print("Cannot find or read example OpenTabulate configuration.", file=sys.stderr)
            sys.exit(1)

        print("Copying configuration to %s." % def_paths['conf_file'])

        # create configuration directory if it doesn't already exist
        os.makedirs(def_paths['conf_dir'], exist_ok=True)

        # write example configuration file
        with open(def_paths['conf_file'], 'wb') as outfile, open(conf_example, 'rb') as infile:
            outfile.write(infile.read())

        print("Done.")
        sys.exit(0)

    # load and validate configuration
    try:
        config.load()
        config.validate()
    except ConfigError as conf_err:
        print("Configuration error: %s" % conf_err, file=sys.stderr)
        sys.exit(1)
    except Exception as err: # other errors (such as loading file)
        print("Error: %s" % err, file=sys.stderr)
        sys.exit(1)
   
    root_dir = config.get('general', 'root_directory')

    # check that root directory is an absolute path
    try:
        assert os.path.isabs(os.path.expanduser(root_dir))
    except AssertionError:
        print("Configuration error: root directory must be an absolute path",
              file=sys.stderr)
        sys.exit(1)
        
    if p_args.initialize == True:
        # try to populate root directory with folders (also validate
        # its creation and contents)
        try:
            os.makedirs(root_dir, exist_ok=True)
        except FileExistsError:
            print(root_dir, "is a file.", file=sys.stderr)
            sys.exit(1)
            
        os.chdir(root_dir)

        if len(os.listdir()) != 0:
            print("OpenTabulate data directory is non-empty, cannot initialize.",
                  file=sys.stderr)
            sys.exit(1)
        else:
            print("Populating OpenTabulate data directory...")
            for directory in data_folders:
                os.makedirs(directory)
            print("Finished creating directories at: %s" % os.getcwd())
            sys.exit(0)

    # clear cache and exit if --clear-cache flag is set
    if p_args.clear_cache == True:
        print("Clearing cache.")
        for manager in cache_mgrs:
            manager.write_cache() # this writes an empty cache
        sys.exit(0)

    # update SOURCE paths to absolute paths *BEFORE* changing current working directory
    for i in range(len(p_args.SOURCE)):
        p_args.SOURCE[i] = os.path.realpath(p_args.SOURCE[i])
        
    # check that OpenTabulate's root directory exists
    try:
        os.chdir(root_dir)
    except (FileNotFoundError, NotADirectoryError):
        print("Error: configured OpenTabulate directory does not exist or"
              " not a directory.", file=sys.stderr)
        sys.exit(1)

    # verify that the data directories are intact
    for directory in data_folders:
        if not os.path.isdir(directory):
            print("Error: data directories are misconfigured.", file=sys.stderr)
            sys.exit(1)

    # now we validate other command-line arguments here
    if p_args.SOURCE == []:
        print("Error: no SOURCE argument specified.", file=sys.stderr)
        sys.exit(1)

    if int(p_args.threads) <= 0:
        print("Error: number of threads must be > 0.", file=sys.stderr)
        sys.exit(1)
    
    log_level_map = {0 : logging.DEBUG,
                     1 : logging.INFO,
                     2 : logging.WARNING,
                     3 : logging.ERROR}

    # override configuration options if command line flags are used 
    if p_args.add_index is not None:
        config['general']['add_index'] = p_args.add_index
        try:
            config.getboolean('general', 'add_index')
        except ValueError:
            print("Error: add index flag must be a boolean value.", file=sys.stderr)
            sys.exit(1)
        
    if p_args.target_enc is not None:
        if p_args.target_enc not in supp_enc:
            print("Error: '%s' is not a supported output encoding." 
                  % p_args.target_enc, file=sys.stderr)
            sys.exit(1)
        else:
            config['general']['target_encoding'] = p_args.target_enc

    if p_args.output_enc_errors is not None:
        if p_args.output_enc_errors not in enc_errs:
            print("Error: '%s' is not an output encoding error handler."
                  % p_args.output_enc_errors)
            sys.exit(1)
        else:
            config['general']['output_encoding_errors'] = p_args.output_enc_errors

    if p_args.clean_ws is not None:
        config['general']['clean_whitespace'] = p_args.clean_ws
        try:
            config.getboolean('general', 'clean_whitespace')
        except ValueError:
            print("Error: clean whitespace flag must be a boolean value.", file=sys.stderr)
            sys.exit(1)

    if p_args.lowercase is not None:
        config['general']['lowercase_output'] = p_args.lowercase
        try:
            config.getboolean('general', 'lowercase_output')
        except ValueError:
            print("Error: lowercase flag must be a boolean value.", file=sys.stderr)
            sys.exit(1)
            
    if p_args.log_level is not None:
        if p_args.log_level in log_level_map:
            logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s',
                                level=log_level_map[p_args.log_level])
        else:
            print("Error: log level must be 0, 1, 2 or 3 (the lower, the more verbose).", 
                  file=sys.stderr)
            sys.exit(1)
    else:
        logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s',
                            level=log_level_map[config.getint('general', 'log_level')])
