"""
...

Written by Maksym Neyra-Nesterenko.
"""

import csv
import subprocess
from os import path

import data_parser
import src_parser
import src_check

myDPI=input()
NO_PROC_FLAG=input()
TOOLS_PATH=path.dirname(path.realpath(__file__))


data = src_parser.parse(myDPI)

if NO_PROC_FLAG == "1":
    exit(0)
else:
    pass

src_check.check(data)    

# - XML FORMAT -
if data['format'] == 'xml':
    es = data_parser.xml_parse(data)
    if es == 1:
        print("[E] Failed to parse XML.")
        exit(1)

# - CSV FORMAT -
elif data['format'] == 'csv':
    # copy raw data into pp (preprocessing)
    subprocess.check_call(['/bin/cp', './raw/' + data['file'], './pp/' + data['file']])
    
    # remove byte order mark from files 
    subprocess.check_call([TOOLS_PATH + '/rmByteOrderMark', './pp/' + data['file']])

    # handle unicode decoding errors before parsing
    #if not UTF8_check('./pp/' + data['file']):
    #    subprocess.check_call([TOOLS_PATH + '/fixCharEncoding', './pp/' + data['file']])

    es = data_parser.csv_parse(data)
    if es == 1:
        print("[E] DPI and CSV field names disagree.")
        exit(1)

print("[!] Data parsing completed.")
