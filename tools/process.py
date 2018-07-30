"""
...

Written by Maksym Neyra-Nesterenko.
"""

import csv
import subprocess
from os import path
from os import remove

import data_parser
import src_parser
import src_pull
import char_encode_check

myDPI=input()
NO_PROC_FLAG=input()
NO_NET_FLAG=input()
TOOLS_PATH=path.dirname(path.realpath(__file__))


# Parse sourcee file
data = src_parser.parse(myDPI)


# Process flag
if NO_PROC_FLAG == "1":
    exit(0)
else:
    pass


# Check integrity / retrieve source file
src_pull.pull(data, NO_NET_FLAG)


# Standardize to CSV
print('[ ] Standardizing data to CSV format . . .')
if data['format'] == 'xml': # XML format
    # Check character encoding
    enc = char_encode_check.check(data)
    parse_metadata = data_parser.xml_parse(data, enc)
    if parse_metadata[0] == 1:
        print("[E] Failed to parse XML.")
        exit(1)
        # 
elif data['format'] == 'csv': # CSV format
    # Check character encoding
    enc = char_encode_check.check(data)
    # copy raw data into pp (preprocessing)
    subprocess.check_call(['/bin/cp', './raw/' + data['file'], './pp/' + data['file']])

    # remove byte order mark from files 
    subprocess.check_call([TOOLS_PATH + '/rmByteOrderMark', './pp/' + data['file']])

    parse_metadata = data_parser.csv_parse(data, enc)
    if parse_metadata[0] == 1:
        print("[E] DPI and CSV field names disagree.")
        remove('./dirty/' + parse_metadata[1])
        exit(1)
else:
    pass
print("[!] Standardization complete.")


# Clean data
print('[ ] Beginning data cleaning...')
subprocess.check_call([TOOLS_PATH + '/rmWhitespace', './dirty/' + parse_metadata[1]])

clean_file = '-'.join(str(x) for x in parse_metadata[1].split('-')[:-1]) + "-CLEAN.csv"

subprocess.check_call(['/bin/mv', './dirty/' + parse_metadata[1], './clean/' + clean_file])

print('[!] Data cleaning complete.')
print('[!] Data processing complete.')
