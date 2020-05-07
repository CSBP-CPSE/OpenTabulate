# -*- coding: utf-8 -*-
"""
Command line argument parser and handler for the OpenTabulate console script.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import os
import sys
import argparse


def parse_arguments():
    """
    Define the command line argument structure and parse it.
    """
    cmd_args = argparse.ArgumentParser(
        description='OpenTabulate: a command-line data tabulation tool.'
    )
    cmd_args.add_argument('-s', '--verify-source', action='store_true', default=False, \
                          help='validate source files without processing data')
    cmd_args.add_argument('-l', '--log-level', action='store', default=None, type=int, metavar='N', \
                          help='specify data processing log verbosity')
    cmd_args.add_argument('--initialize', action='store_true', \
                          help='create processing directories')
    #cmd_args.add_argument('-t', '--print-trace', action='store_true', \
    #                      help='print traceback of errors')

    cmd_args.add_argument('SOURCE', nargs='*', default=None, help='path to source file')
    return cmd_args.parse_args()


def validate_arguments(p_args, config):
    """
    Validate and perform actions based on the provided command line arguments.

    Note:
        p_args is modified in this method.

    Args:
        p_args (argparse.Namespace): Parsed arguments.
        config (Configuration): OpenTabulate configuration.
    """
    root_dir = config.get('general', 'root_directory')
    data_folders = ('./data', './data/input', './data/output', './sources')
        
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
            print("OpenTabulate data directory is non-empty, cannot initialize",
                  file=sys.stderr)
            sys.exit(1)
        else:
            print("Populating OpenTabulate data directory.")
            for directory in data_folders:
                os.makedirs(directory)
            print("Finished creating directories at: %s" % os.getcwd())
            sys.exit(0)

    # update SOURCE paths to absolute paths *BEFORE* changing current working directory
    for i in range(len(p_args.SOURCE)):
        p_args.SOURCE[i] = os.path.realpath(p_args.SOURCE[i])
        
    # check that OpenTabulate's root directory exists
    try:
        os.chdir(root_dir)
    except (FileNotFoundError, NotADirectoryError):
        print("Error! Configured OpenTabulate directory does not exist or"
              " not a directory.", file=sys.stderr)
        sys.exit(1)

    # verify that the data directories are intact
    for directory in data_folders:
        if not os.path.isdir(directory):
            print("Error! Data directories are misconfigured.", file=sys.stderr)
            sys.exit(1)

    # now we validate other command-line arguments here
    
    if p_args.SOURCE == []:
        print("Error! The following arguments are required: SOURCE", file=sys.stderr)
        sys.exit(1)

    
    log_level_map = {0 : logging.DEBUG,
                     1 : logging.INFO,
                     2 : logging.WARNING,
                     3 : logging.ERROR}
    
    if p_args.log_level is not None:
        if p_args.verbosity in log_level_map:
            logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s',
                                level=log_level_map(p_args.log_level))
        else:
            print("Error! Log level must be 0, 1, 2 or 3 (the lower, the more detailed)", file=sys.stderr)
            sys.exit(1)
    else:
        logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s',
                            level=log_level_map(config.get('general', 'log_level')))
