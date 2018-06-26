"""
* Statistics Canada - Center for Special Business Projects - DEIL *

~ Maksym Neyra-Nesterenko

Verifies that the .json files in format have the right syntax and the correct parameters.
If any of the checks fail, the .json file is not added to the to-be-processed list. 
"""

# -------------
# -- MODULES --
# -------------

import json
import csv
from os import path
import subprocess
import obrparser

# ---------------
# -- FUNCTIONS --
# ---------------

def isEmpty(value):
    # Checks if value is an empty string
    if value == '':
        return True
    else:
        return False

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


# -----------------------
# -- PROCESSING SCRIPT --
# -----------------------

SRC_PATH = input()
TOOLS_PATH = path.dirname(path.realpath(__file__))

# safeguard depending on how you obtain the
# data processing instruction file paths
if not path.exists(SRC_PATH):
    print("[E] Input path does not exist >", SRC_PATH)
    exit(1)
# Parse .json file
try:
    with open(SRC_PATH) as f:
        data = json.load(f)
except ValueError: # failed parse
    print("[E] Wrong JSON format for DPI >", SRC_PATH)
    exit(1)
# These fields must exist and be non-empty in the format file!
try:
    if isEmpty(data['type']):
        print("[E] Missing 'type' > ", SRC_PATH)
        exit(1)
    if data['type'] == 'xml':
        if isEmpty(data['filename']) or \
           isEmpty(data['header']) or \
           isEmpty(data['info']['name']):
            print("[E] Missing required field >", SRC_PATH)
            exit(1)
    elif data['type'] == 'csv':
        if isEmpty(data['filename']) or \
           isEmpty(data['info']['name']):
            print("[E] Missing required field >", SRC_PATH)
            exit(1)
    else:
        print("[E] Unsupported data format '", data['type'],"' > ", SRC_PATH, sep='')
        exit(1)
    if not (isinstance(data['info']['address'], dict)):
        print("[E] Address entry is not a list >", SRC_PATH)
        exit(1)
    for i in data['info']['address']:
        if not (i in obrparser.ADDR_FIELD_LABEL):
            print("[E] Address entry contains an invalid field type >", SRC_PATH)
            exit(1)
except KeyError: # semantic error
    print("[E] Missing REQUIRED field >", SRC_PATH)
    exit(1)

if not path.exists('./raw/' + data['filename']):
    print("[E] 'filename' not found in raw folder > ", SRC_PATH)
    exit(1)

print("[ ] DPI check passed > ", SRC_PATH)

if data['type'] == 'xml':
    es = obrparser.xml_parse(data)
    if es == 1:
        print("[E] Failed to parse XML >", SRC_PATH)
        exit(1)
    if es == 2:
        print("[E] Missing element in header >", SRC_PATH)
        exit(1)
elif data['type'] == 'csv':
    # remove byte order mark from files 
    subprocess.check_call([TOOLS_PATH + '/rmByteOrderMark', './raw/' + data['filename'], './pp/' + data['filename']])
    # handle unicode decoding errors before parsing
    if not UTF8_check('./pp/' + data['filename']):
        subprocess.check_call([TOOLS_PATH + '/fixCharEncoding', './pp/' + data['filename']])

    es = obrparser.csv_parse(data)
    if es == 1:
        print("[E] DPI and CSV field names disagree >", SRC_PATH)
        exit(1)

print("[!] Successful process >", SRC_PATH)
