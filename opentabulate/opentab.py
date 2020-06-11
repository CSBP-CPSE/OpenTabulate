# -*- coding: utf-8 -*-
"""
The OpenTabulate command-line tool. This script is used as a console script entry 
point for setuptools.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
Center for Special Business Projects (CSBP) at Statistics Canada.
"""
import logging
import os
import sys
import time

from opentabulate.args import parse_arguments, validate_args_and_config
from opentabulate.config import Configuration
from opentabulate.cache import CacheManager
from opentabulate.opentab_funcs import parse_source_file, process

def main():
    config = Configuration()
    parsed_args = parse_arguments()
    cache_mgr = CacheManager()
    
    validate_args_and_config(parsed_args, config, cache_mgr)

    # parse source files
    source_list = parse_source_file(parsed_args, config)

    # exit if --verify-source flag is set
    if parsed_args.verify_source == True:
        sys.exit(0)

    # start data processing
    print("Beginning data processing.")

    try:
        cache_mgr.read_cache()
    except IOError as io_err:
        print(io_err, file=sys.stderr)
        sys.exit(1)

    start_time = time.perf_counter()
    
    proc_results = []

    for source in source_list:
        source_log = logging.getLogger(source.localfile)
        current_digest = cache_mgr.compute_hash(source.input_path)
        source_log.debug("Computed digest: %s" % current_digest)
        if parsed_args.ignore_cache == False:
            idx, _, cached_digest = cache_mgr.query(source.localfile)
            source_log.debug("Cached digest: %s" % cached_digest)
            if idx is not None: # data appears in cache
                if not os.path.exists(source.output_path): # output is missing
                    source_log.debug("Output data is missing, processing anyway")
                    rcode = process(source)
                elif cached_digest != current_digest: # hashes differ
                    source_log.debug("Hash digests differ, proceeding with processing")
                    rcode = process(source)
                else: # hashes are the same
                    source_log.debug("Hash digests are equal, processing omitted")
                    rcode = 0
            else: # data is not in cache
                source_log.debug("Processing due to absense of cache")
                rcode = process(source)
        else:
            source_log.debug("Processing, ignoring cache")
            rcode = process(source)
        
        if rcode == 0: # update cache if processing is successful
            cache_mgr.insert(source.localfile, current_digest)

        proc_results.append(rcode)
        
    end_time = time.perf_counter()

    try:
        cache_mgr.write_cache()
    except IOError as io_err:
        print("Error: %s" % io_err, file=sys.stderr)
        # do not exit here

    print("Completed processing in", end_time - start_time, "seconds.")

    # display detected errors
    errors_detected = False
    for i in range(0,len(parsed_args.SOURCE)):
        if proc_results[i] != 0:
            errors_detected = True
            break

    if errors_detected:
        print("Error occurred during processing of:") 
        for i in range(0,len(source_list)):
            if proc_results[i] != 0:
                print("  *!*", source_list[i].localfile)
        print("Please refer to the [ERROR] log messages during output.")

    
if __name__ == '__main__':
    main()
