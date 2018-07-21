"""
A workflow script that handles preprocessing and calls obrparser.py to perform data processing.

This script parses the source files in JSON format and extracts the metadata for data processing. 
The metadata must follow syntactic rules, otherwise if any of the rules are violated, the script 
exits with a non-zero exit status.

Written by Maksym Neyra-Nesterenko.
"""

# -------------
# -- MODULES --
# -------------

import json
import csv
from os import path
import subprocess
import obrparser

# ----------------------
# -- HELPER FUNCTIONS --
# ----------------------

def isEmpty(value):
    # Checks if value is an empty string
    if value == '':
        print("[E] Empty required tag >", SRC_PATH)
        exit(1)

"""        
def UTF8_check(path_to_file):
    # A heuristic verification of whether or not a file uses the utf-8 encoding
    source_dataset = open(path_to_file, 'r', encoding='utf-8', newline='')
    reader = csv.reader(source_dataset)
    try:
        for row in reader:
            str(row)
    except UnicodeDecodeError:
        return False
    return True
"""

# -----------------------
# -- PROCESSING SCRIPT --
# -----------------------

SRC_PATH = input()
NO_PROC_STR = input()
TOOLS_PATH = path.dirname(path.realpath(__file__))
URL_FLAG = False

if NO_PROC_STR == "T":
    NO_PROC_FLAG = True
elif NO_PROC_STR == "F":
    NO_PROC_FLAG = False
else:
    print("[E] NO_PROC_STR not correctly set.")
    exit(1)
    
# safeguard depending on how you obtain the
# data processing instruction file paths
if not path.exists(SRC_PATH):
    print("[E] Input path does not exist >", SRC_PATH)
    exit(1)
# parse .json file
try:
    with open(SRC_PATH) as f:
        data = json.load(f)
except ValueError: # failed parse
    print("[E] Wrong JSON format for DPI >", SRC_PATH)
    exit(1)
# require source files to contain required fields with non-empty tags
try:
    if isEmpty(data['type']):
        print("[E] Missing tag 'type' > ", SRC_PATH)
        exit(1)

    if ('url' in data) and ('filename' in data):
        print("[E] Cannot have both 'url' and 'filename' tags in >", SRC_PATH)
        exit(1)
    elif ('url' in data) and ('filename' not in data):
        URL_FLAG = True
    elif ('url' not in data) and ('filename' in data):
        URL_FLAG = False
    else:
        print("[E] Missing required tag 'url/filename' >", SRC_PATH)
        exit(1)

# -------

# URL handling goes here

# -------

    if data['type'] == 'xml':
        if URL_FLAG == True:
            isEmpty(data['url'])
        else:
            isEmpty(data['filename'])
        isEmpty(data['header'])
    elif data['type'] == 'csv':
        if URL_FLAG == True:
            isEmpty(data['url'])
        else:
            isEmpty(data['filename'])
    else:
        print("[E] Unsupported data format '", data['type'],"' > ", SRC_PATH, sep='')
        exit(1)
    if 'address' in data['info']:
        if not (isinstance(data['info']['address'], dict)):
            print("[E] Address tag is not a list >", SRC_PATH)
            exit(1)
        for i in data['info']['address']:
            if not (i in obrparser.ADDR_FIELD_LABEL):
                print("[E] Address tag contains an invalid key >", SRC_PATH)
                exit(1)
    if 'force' in data:
        if not (isinstance(data['force'], dict)):
            print("[E] Force tag is not a list >", SRC_PATH)
            exit(1)
        for i in data['force']:
            if not (i in obrparser.FORCE_LABEL):
                print("[E] Force tag contains an invalid key >", SRC_PATH)
                exit(1)
            elif i in data['info']['address']:
                print("[E] The key '", i, "' appears in both 'force' and 'address' >", SRC_PATH)
                exit(1)
        
except KeyError: # missing field error
    print("[E] Missing required tag >", SRC_PATH)
    exit(1)

if not path.exists('./raw/' + data['filename']):
    print("[E] 'filename' not found in raw folder > ", SRC_PATH)
    exit(1)

print("[ ] DPI check passed > ", SRC_PATH)

if NO_PROC_FLAG == True:
    exit(0)

# --------------
# - XML FORMAT -
# --------------
if data['type'] == 'xml':
    es = obrparser.xml_parse(data)
    if es == 1:
        print("[E] Failed to parse XML >", SRC_PATH)
        exit(1)
# --------------
# - CSV FORMAT -
# --------------        
elif data['type'] == 'csv':
    # copy raw data into pp (preprocessing)
    subprocess.check_call(['/bin/cp', './raw/' + data['filename'], './pp/' + data['filename']])
    
    # remove byte order mark from files 
    subprocess.check_call([TOOLS_PATH + '/rmByteOrderMark', './pp/' + data['filename']])

    # handle unicode decoding errors before parsing
    #if not UTF8_check('./pp/' + data['filename']):
    #    subprocess.check_call([TOOLS_PATH + '/fixCharEncoding', './pp/' + data['filename']])

    es = obrparser.csv_parse(data)
    if es == 1:
        print("[E] DPI and CSV field names disagree >", SRC_PATH)
        exit(1)

print("[!] Data parsing completed.")
