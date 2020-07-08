# -*- coding: utf-8 -*-
"""
The OpenTabulate command-line tool. This script is used as a console script entry 
point for setuptools.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
Center for Special Business Projects (CSBP) at Statistics Canada.
"""
import logging
import os
import signal
import sys
import time

from opentabulate.args import parse_arguments, validate_args_and_config
from opentabulate.config import Configuration
from opentabulate.cache import CacheManager
from opentabulate.opentab_funcs import parse_source_file
from opentabulate.thread import ThreadPool

def main():
    config = Configuration()
    parsed_args = parse_arguments()
    input_cache_mgr = CacheManager(os.path.expanduser('~') + '/.cache/opentabulate/data_hashes.txt')
    src_cache_mgr = CacheManager(os.path.expanduser('~') + '/.cache/opentabulate/src_hashes.txt')
    
    validate_args_and_config(parsed_args, config, [input_cache_mgr, src_cache_mgr])

    # parse source files
    source_list = parse_source_file(parsed_args, config)

    # exit if --verify-source flag is set
    if parsed_args.verify_source == True:
        sys.exit(0)

    # start data processing
    print("Beginning data processing.")

    try:
        input_cache_mgr.read_cache()
        src_cache_mgr.read_cache()
    except IOError as io_err:
        print(io_err, file=sys.stderr)
        sys.exit(1)

    proc_sources = []
    src_digests = []
    data_digests = []

    for source in source_list:
        source_log = logging.getLogger(source.localfile)

        current_input_digest = input_cache_mgr.compute_hash(source.input_path)
        current_src_digest = src_cache_mgr.compute_hash(source.src_path)
        
        source_log.debug("Computed source file digest: %s" % current_src_digest)
        source_log.debug("Computed input data digest: %s" % current_input_digest)
       
        if parsed_args.ignore_cache == False:
            s_idx, _, cached_src_digest = src_cache_mgr.query(source.src_path)
            d_idx, _, cached_input_digest = input_cache_mgr.query(source.localfile)

            source_log.debug("Cached source file digest: %s" % cached_src_digest)
            source_log.debug("Cached input data digest: %s" % cached_input_digest)

            add_to_proc = False

            if not os.path.exists(source.output_path): # output is missing
                source_log.debug("Output data is missing, proceeding anyway")
                add_to_proc = True
            elif (s_idx is None) or (d_idx is None): # hashes are not in cache
                source_log.debug("Processing due to absense of cached digest")
                add_to_proc = True
            elif (cached_src_digest != current_src_digest) or \
                 (cached_input_digest != current_input_digest): # hashes differ
                source_log.debug("A pair of hash digests differ, proceeding with processing")
                add_to_proc = True
            else: # hashes are the same
                source_log.debug("Both pairs of hash digests are equal, processing omitted")
                add_to_proc = False

            if add_to_proc:
                proc_sources.append(source)
                src_digests.append(current_src_digest)
                data_digests.append(current_input_digest)
        
        else:
            source_log.debug("Processing, ignoring cache")
            proc_sources.append(source)
            src_digests.append(current_src_digest)
            data_digests.append(current_input_digest)

    
    start_time = time.perf_counter()
    
    with ThreadPool(proc_sources, num_threads=parsed_args.threads) as pool: # need num_threads to be command line args
        pool.execute_threads()
        proc_results = pool.get_rcodes()

    end_time = time.perf_counter()

    
    for i in range(len(proc_sources)):
        if proc_results[i] == 0: # update cache if processing is successful
            src_cache_mgr.insert(proc_sources[i].src_path, src_digests[i])
            input_cache_mgr.insert(proc_sources[i].localfile, data_digests[i])

    try:
        src_cache_mgr.write_cache()
        input_cache_mgr.write_cache()
    except IOError as io_err:
        print("Error: %s" % io_err, file=sys.stderr)
        # do not exit here

    print("Completed processing in", end_time - start_time, "seconds.")

    # display detected errors
    errors_detected = False
    incomplete_detected = False
    
    for val in proc_results:
        if val != 0:
            errors_detected = True
            break

    for val in proc_results:
        if val is None:
            incomplete_detected = True
            break
    
    if errors_detected:
        print("Error occurred during processing of:", file=sys.stderr) 
        for i in range(len(proc_sources)):
            if proc_results[i] == 1:
                print("  *!*", proc_sources[i].localfile, file=sys.stderr)
        print("Please refer to the [ERROR] log messages during output.", file=sys.stderr)

    if incomplete_detected:
        print("Sources listed below never processed or finished due to interrupt:", file=sys.stderr)
        for i in range(len(proc_sources)):
            if proc_results[i] is None:
                print(" *x*", proc_sources[i].localfile, file=sys.stderr)
    
if __name__ == '__main__':
    main()
