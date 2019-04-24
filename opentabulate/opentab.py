# -*- coding: utf-8 -*-
"""
A command-line tool that interfaces the OpenTabulate API.

This script is used as a console script entry point for setuptools. It aims to 
serve as a OpenTabulate API pipeline and command line tool, with support for 
verbose logging and multiprocessing.

Created and written by Maksym Neyra-Nesterenko.

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""

import argparse
import logging
import multiprocessing
import os
import platform
import sys
import time
import traceback

import opentabulate.tabulate as tabulate

########################
# FUNCTIONS FOR MAIN() #
########################

def _parse_cmd_args():
    """
    Parse command line arguments using the argparse module.

    Returns:
        argparse.Namespace: Parsed arguments with positional and optional parameters.
    """
    cmd_args = argparse.ArgumentParser(description='OpenTabulate: a command-line data tabulation tool.')
    cmd_args.add_argument('-p', '--ignore-proc', action='store_true', default=False, \
                          help='check source files without processing data')
    cmd_args.add_argument('-u', '--ignore-url', action='store_true', default=False, \
                          help='ignore "url" entries from source files')
    cmd_args.add_argument('-z', '--no-decompress', action='store_true', default=False, \
                          help='do not decompress files from compressed archives')
    cmd_args.add_argument('--pre', action='store_true', default=False, \
                          help='allow preprocessing script to run')
    cmd_args.add_argument('--post', action='store_true', default=False, \
                          help='allow postprocessing script to run')
    cmd_args.add_argument('-j', '--jobs', action='store', default=1, type=int, metavar='N', \
                          help='run at most N jobs asynchronously')
    cmd_args.add_argument('-v', '--verbose', action='store_true',
                          help='enable debug mode printing')
    cmd_args.add_argument('--initialize', action='store_true', default=False, \
                          help='create processing directories')
    cmd_args.add_argument('SOURCE', nargs='*', default=None, help='path to source file')
    return cmd_args.parse_args()


def _args_handler(p_args):
    """
    Perform actions based on parsed arguments.

    Note:
        p_args is modified in this method.

    Args:
        p_args (argparse.Namespace): Parsed arguments.
    """
    # get absolute paths
    for i in range(0,len(p_args.SOURCE)):
        p_args.SOURCE[i] = os.path.abspath(p_args.SOURCE[i])

    root_path = os.path.expanduser('~') + '/.opentabulate'

    if p_args.initialize == True:
        if not os.path.exists(root_path):
            os.makedirs(root_path)
            os.chdir(root_path)
        else:
            print("OpenTabulate root directory already exists.", file=sys.stderr)
            exit(1)

        PD_TREE = ['./pddir', './pddir/raw', './pddir/pre', './pddir/dirty',
                       './pddir/clean', './sources', './scripts']

        print("Creating data processing directory tree in current working directory...")
        for p in PD_TREE:
            if not os.path.isdir(p):
                os.makedirs(p)
        print("Finished creating directories")
        exit(0)

    # check that opentabulate directory exists
    try:
        os.chdir(root_path)
    except FileNotFoundError:
        print("OpenTabulate root directory does not exist.",
              "Use --initialize flag?", file=sys.stderr)
        exit(1)    
    
    if p_args.SOURCE == []:
        print("Error! The following arguments are required: SOURCE", file=sys.stderr)
        exit(1)

    if p_args.jobs < 1:
        print("Error! Jobs should be a positive integer", file=sys.stderr)
        exit(1)

    if p_args.verbose:
        logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s', level=logging.DEBUG)
        print("Running in debug mode (verbose output)")
    else:
        logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s', level=logging.WARNING)


def _parse_src(p_args, SRC, URLS):
    """
    Parse sources obtained from parsed arguments.

    Note:
        SRC and URLS are modified in this method.

    Args:
        p_args (argparse.Namespace): Parsed arguments.
        SRC (list): List of Source objects.
        URLS (list): List of (URL) strings.
    """
    srclog = logging.getLogger('source')
    
    for source in p_args.SOURCE:
        srclog.debug("Creating source object: %s" % source)
        srcfile = tabulate.Source(source, p_args.pre, p_args.post, p_args.ignore_url, \
                             p_args.no_decompress)
        srclog.debug("Parsing contents...")
        srcfile.parse()
        srclog.debug("Passed")

        if 'url' not in srcfile.metadata:
            srclog.warning("'%s' does not have a URL." % source)
        elif ('url' in srcfile.metadata) and (srcfile.metadata['url'] not in URLS):
            srcfile.fetch_url()
            URLS.append(srcfile.metadata['url'])

        if 'compression' in srcfile.metadata:
            srcfile.archive_extraction()

        SRC.append(srcfile)


def _process(source, parse_address):
    """
    Process data referenced by a Source object and optionally use an address 
    parsing function.

    Args:
        source (Source): Dataset abstraction.
        parse_address (function): Address parsing function, input must be
            a string.

    Returns:
        int: 1 if an error occurred, 0 otherwise.
    """
    pool_worker_id = multiprocessing.current_process().name
    prodsys = tabulate.DataProcess(source, parse_address)
    srclog = logging.getLogger(source.local_fname)

    if not prodsys.source.pre_flag and 'pre' in source.metadata:
        srclog.error("Source has 'pre' key but --pre flag not used as argument")
        return 1
    if not prodsys.source.post_flag and 'post' in source.metadata:
        srclog.error("Source has 'post' key but --post flag not used as argument")
        return 1

    srclog.debug("Starting tabulation for '%s'" % prodsys.source.local_fname)

    if prodsys.source.pre_flag and 'pre' in source.metadata:
        srclog.warning("Running 'preprocessData()' method due to --pre flag and 'pre' key")
        prodsys.preprocessData()
        srclog.warning("Completed 'preprocessData()'")

    srclog.debug("Calling 'prepareData()'")
    prodsys.prepareData()
    srclog.debug("Done")
    srclog.debug("Calling 'extractLabels()'")
    prodsys.extractLabels()
    srclog.debug("Done")
    srclog.debug("Initiating 'parse()' method...")

    try:
        prodsys.parse()
    except Exception:
        srclog.error("An exception in parse() has occurred.")
        traceback.print_exc()
        return 1

    srclog.debug("Completed")
    srclog.debug("Initiating 'clean()' method...")
    prodsys.clean()
    srclog.debug("Completed")

    if prodsys.source.post_flag and 'post' in source.metadata:
        srclog.warning("Running 'postprocessData()' due to --post flag and 'post' key")
        prodsys.postprocessData()
        srclog.warning("Completed 'postprocessData()'")

    srclog.debug("Tabulating '%s' complete." % prodsys.source.local_fname)
    return 0


################
# MAIN() BLOCK #
################

def main():
    args = _parse_cmd_args()
    _args_handler(args)

    if input('Process data? (enter yes in capital letters): ') != 'YES':
        print("Exiting.")
        exit(1)
    
    src = []
    url = []

    _parse_src(args, src, url)

    # exit if processing 
    if args.ignore_proc == True:
        exit(0)

    # --- might wrap this in a function later ---
    # load address parser if 'full_addr' key exists
    for so in src:
        if 'full_addr' in so.metadata['info']:
            logging.info("Loading address parser module...")
            try:
                from postal.parser import parse_address
            except ImportError:
                logging.error("Failed to load address parser module")
                exit(1)
            logging.info("Finished loading libpostal address parser")
            break
        else:
            parse_address = None
    # --- ----------------------------------- ---

    print("Beginning data processing, please standby or grab a coffee. :-)")

    start_time = time.perf_counter()

    # if __name__ == '__main__':
    # 
    # ^ Although this line is recommended for multiprocessing, it is commented 
    # out to operate properly with the console script entry point defined in
    # "setup.py". For portability to Windows in the future, this may need to
    # be revisited. :-)
    with multiprocessing.Pool(processes=args.jobs) as pool:
        # pool function calls of process.py here
        jobs = []
        for source in src:
            jobs.append(pool.apply_async(_process, (source, parse_address)))
        # wait for jobs to finish
        results = []
        for pool_proc in jobs:
            results.append(pool_proc.get())

    end_time = time.perf_counter()            

    print("Completed pool work in", end_time - start_time, "seconds.")

    errors_detected = False

    for i in range(0,len(src)):
        if results[i] != 0:
            errors_detected = True
            break

    if errors_detected:
        print("Error occurred during processing of:") 
        for i in range(0,len(src)):
            if results[i] != 0:
                print("  *!*", src[i].local_fname)
        print("Please refer to the [ERROR] tagged messages during output.")

    print("Data processing complete.")
    # end of main()

if __name__ == '__main__':
    main()
