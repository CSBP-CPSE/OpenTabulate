# system modules
import csv
import subprocess
import sys
import io
import time

from os import path

# local modules
import data_parser
import src_parser
import char_encode_check


def _iostr_output(proc_log):
    sys.stdout = sys.__stdout__
    s = proc_log.getvalue()
    proc_log.close()
    return s


def process(source, ignore_proc, ignore_url, address_parser):
    proc_log = io.StringIO()
    sys.stdout = proc_log

    # parse source file / retrieve url / check existence of data
    srcdata = src_parser.parse(source, ignore_url)
    if srcdata == None:
        return _iostr_output(proc_log)

    # ignore processing?
    if ignore_proc == True:
        return _iostr_output(proc_log)

    std_start_time = time.perf_counter()
    
    # Standardize to CSV
    print('[ ] Standardizing data to CSV format . . .')
    if srcdata['format'] == 'xml': # XML format
        # Check character encoding
        enc = char_encode_check.check(srcdata)
        if enc == None:
            return _iostr_output(proc_log)
        parse_metadata = data_parser.xml_parse(srcdata, enc, address_parser)
        if parse_metadata == None:
            return _iostr_output(proc_log)

    elif srcdata['format'] == 'csv': # CSV format
        # Check character encoding
        enc = char_encode_check.check(srcdata)
        if enc == None:
            return _iostr_output(proc_log)

        # copy raw data into pp (preprocessing) while filling in erroneous entries
        data_parser.pp_format_correction(srcdata['file'], enc)

        # remove byte order mark from files 
        subprocess.check_call(['./tools/rmByteOrderMark', './pddir/pp/' + srcdata['file']])

        parse_metadata = data_parser.csv_parse(srcdata, "utf-8", address_parser)
        if parse_metadata == None:
            return _iostr_output(proc_log)
    else:
        pass
    print("[!] Standardization complete.")

    # Clean data
    print('[ ] Beginning data cleaning...')

    clean_file = '-'.join(str(x) for x in parse_metadata.split('-')[:-1]) + "-CLEAN.csv"

    subprocess.check_call(['/bin/mv', './pddir/dirty/' + parse_metadata, './pddir/clean/' + clean_file])

    data_parser.blank_fill('./pddir/clean/' + clean_file)

    std_end_time = time.perf_counter()

    print('[!] Data cleaning complete.')
    print('[!] Processed dataset in', std_end_time - std_start_time, 'seconds.')

    return _iostr_output(proc_log)
