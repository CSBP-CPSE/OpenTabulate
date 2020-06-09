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

    validate_args_and_config(parsed_args, config)

    # clear cache and exit if --clear-cache flag is set
    if parsed_args.clear_cache == True:
        logging.info("Clearing cache.")
        cache_mgr.write_cache() # this writes an empty cache
        sys.exit(0)

    # parse source files
    source_list = parse_source_file(parsed_args, config)

    # exit if --verify-source flag is set
    if parsed_args.verify_source == True:
        sys.exit(0)

    # start data processing
    logging.info("Beginning data processing.")

    cache_mgr.read_cache()

    start_time = time.perf_counter()
    
    proc_results = []
    
    for source in source_list:
        current_digest = cache_mgr.compute_hash(source.input_path)
        logging.info("Computed digest of %s: %s" % (source.localfile, current_digest))
        if parsed_args.ignore_cache == False:
            idx, _, cached_digest = cache_mgr.query(source.localfile)
            logging.info("Cached digest of %s: %s" % (source.localfile, cached_digest))
            if idx is not None: # data appears in cache
                if not os.path.exists(source.output_path): # output is missing
                    logging.info("Output data is missing, processing anyway")
                    rcode = process(source)
                elif cached_digest != current_digest: # hashes differ
                    logging.info("Hash digests differ")
                    rcode = process(source)
                else: # hashes are the same
                    logging.info("Hash digests are equal")
                    rcode = 0
            else: # data is not in cache
                logging.info("Processing due to absense of cache")
                rcode = process(source)
        else:
            logging.info("Processing, ignoring cache")
            rcode = process(source)
        
        if rcode == 0: # update cache if processing is successful
            cache_mgr.insert(source.localfile, current_digest)

        proc_results.append(rcode)
        
    end_time = time.perf_counter()

    cache_mgr.write_cache()

    print("Completed pool work in", end_time - start_time, "seconds.")

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
        print("Please refer to the [ERROR] tagged messages during output.")

    print("Data processing complete.")

    
if __name__ == '__main__':
    main()
