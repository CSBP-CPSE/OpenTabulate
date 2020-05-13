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
from opentabulate.opentab_funcs import parse_source_file, process

def main():
    config = Configuration()
    parsed_args = parse_arguments()

    validate_args_and_config(parsed_args, config)

    # parse source files
    source_list = parse_source_file(parsed_args, config)

    # exit if --verify-source flag is set
    if parsed_args.verify_source == True:
        sys.exit(0)

    # start data processing
    logging.info("Beginning data processing.")

    start_time = time.perf_counter()
    
    proc_results = []
    for source in source_list:
        rcode = process(source)
        proc_results.append(rcode)
        
    end_time = time.perf_counter()

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
