# -*- coding: utf-8 -*-
"""
OpenTabulate command line script wrapper functions.

The functions provided define the data processing pipeline.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import logging
import sys
import traceback
import opentabulate.tabulate as tabulate

def parse_source_file(p_args, config):
    """
    Create Source objects and parse the corresponding source file.

    Args:
        p_args (argparse.Namespace): Parsed arguments.
        config (Configuration): OpenTabulate configuration file.

    Returns:
        src_objects (list): List of (parsed) Source objects.
    """
    src_objects = list()
    src_errors = dict()
    
    src_log = logging.getLogger('source')
    
    for source_path in p_args.SOURCE:
        src_log.debug("Creating source object: %s" % source_path)
        source = tabulate.Source(source_path, p_args, config)
        src_log.debug("Verifying source: %s" % source_path)
        try:
            source.parse()
        except Exception as src_parse_error:
            src_log.debug(src_parse_error)
            src_errors[source_path] = str(src_parse_error)

        if source_path not in src_errors:
            src_log.debug("Passed")

        src_objects.append(source)

    if len(src_errors) != 0:
        src_log.error("Errors were found in some of the source files parsed.")
        
        for source_path in src_errors:
            src_log.error("SOURCE: %s" % source_path)
            src_log.error(src_errors[source_path])
            
        print("Fix these errors to process the source files!", file=sys.stderr)
        sys.exit(1)
    else:
        return src_objects


def process(source):
    """
    Process and tabulate the data referenced by a Source object.

    Args:
        source (Source): Dataset processing configuration and metadata.

    Returns:
        int: 1 if an error occurred, 0 otherwise.
    """
    pipeline = tabulate.DataProcess(source)
    source_log = logging.getLogger(source.localfile)

    source_log.debug("Tabulating '%s'" % pipeline.source.localfile)

    source_log.debug("Configuring algorithm objects ( pipeline.prepareData() )")
    pipeline.prepareData()

    source_log.debug("Configuring output column names ( pipeline.extractLabels() )")
    pipeline.constructLabelMap()
    
    source_log.debug("Tabulating data ( pipeline.tabulate() )")
    try:
        pipeline.tabulate()
    except Exception as e:
        source_log.error("Error during tabulation: %s." % e)
        traceback.print_exc()
        return 1

    source_log.debug("Completed tabulation of '%s'" % pipeline.source.localfile)
    return 0
