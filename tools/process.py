# system modules
import csv
import subprocess

from os import path
from os import remove

# local modules
import data_parser
import src_parser
import char_encode_check


def process(source, ignore_proc, ignore_url, address_parser):
    # parse source file / retrieve url / check existence of data
    srcdata = src_parser.parse(source, ignore_url)
    if srcdata == None:
        return None
    # ignore processing?
    if ignore_proc == True:
        return True
    # Standardize to CSV
    print('[ ] Standardizing data to CSV format . . .')
    if srcdata['format'] == 'xml': # XML format
        # Check character encoding
        enc = char_encode_check.check(srcdata)
        parse_metadata = data_parser.xml_parse(srcdata, enc, address_parser)
        if parse_metadata[0] == 1:
            print("[E] Failed to parse XML.")
            return None

    elif srcdata['format'] == 'csv': # CSV format
        # Check character encoding
        enc = char_encode_check.check(srcdata)
        # copy raw data into pp (preprocessing)
        subprocess.check_call(['/bin/cp', './pddir/raw/' + srcdata['file'], './pddir/pp/' + srcdata['file']])

        # remove byte order mark from files 
        subprocess.check_call(['./tools/rmByteOrderMark', './pddir/pp/' + srcdata['file']])

        parse_metadata = data_parser.csv_parse(srcdata, enc, address_parser)
        if parse_metadata[0] == 1:
            print("[E] DPI and CSV field names disagree.")
            remove('./pddir/dirty/' + parse_metadata[1])
            return None
    else:
        pass
    print("[!] Standardization complete.")

    # Clean data
    print('[ ] Beginning data cleaning...')
    subprocess.check_call(['./tools/rmWhitespace', './pddir/dirty/' + parse_metadata[1]])

    clean_file = '-'.join(str(x) for x in parse_metadata[1].split('-')[:-1]) + "-CLEAN.csv"

    subprocess.check_call(['/bin/mv', './pddir/dirty/' + parse_metadata[1], './pddir/clean/' + clean_file])

    print('[!] Data cleaning complete.')
    print('[!] Data processing complete.')
    return True
