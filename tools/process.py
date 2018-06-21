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

def isEmpty(value): # Checks if value is an empty string
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
    print("ERROR: DPI does not exist! ->", SRC_PATH)
    exit(1)
# Parse .json file
try:
    with open(SRC_PATH) as f:
        data = json.load(f)
except ValueError: # failed parse
    print("ERROR: Failed to parse DPI ->", SRC_PATH)
    exit(1)
# These fields must exist and be non-empty in the format file!
try:
    if isEmpty(data['filename']) or \
       isEmpty(data['type']) or \
       isEmpty(data['info']['header']) or \
       isEmpty(data['info']['name']) or \
       isEmpty(data['info']['address']):
        print("ERROR: Contains an empty field ->", SRC_PATH)
        exit(1)
except KeyError: # semantic error
    print("ERROR: Missing required field ->", SRC_PATH)
    exit(1)

# Check for existence of 'filename' in the raw directory
if not path.exists('./raw/' + data['filename']):
    print("ERROR: DPI filename not found in 'raw'! ->", SRC_PATH)
    exit(1)

print("Acceptable syntax:", SRC_PATH)

if data['type'] == 'xml':
    es = obrparser.xml_parse(data)
    if es == 1:
        print("ERROR: Could not parse XML file ->", SRC_PATH)
    elif es == 2:
        print("ERROR: Could not find XML file in preprocessing ->", SRC_PATH)
elif data['type'] == 'csv':
    # remove byte order mark from files 
    subprocess.check_call([TOOLS_PATH + '/rmByteOrderMark', './raw/' + data['filename'], './pp/' + data['filename']])
    # handle unicode decoding errors before parsing
    if not UTF8_check('./pp/' + data['filename']):
        subprocess.check_call([TOOLS_PATH + '/fixCharEncoding', './pp/' + data['filename']])
    es = obrparser.csv_parse(data)
    if es == 1:
        print("ERROR: Could not find CSV file in preprocessing ->", SRC_PATH)
    elif es == 2:
        print("ERROR: DPI fields and CSV column names disagree ->", SRC_PATH)
