"""
* Statistics Canada - Center for Special Business Projects - DEIL *

~ Maksym Neyra-Nesterenko

Verifies that the .json files in format have the right syntax and the correct parameters.
If any of the checks fail, the .json file is not added to the to-be-processed list. 
"""
import json
from sys import stdin
from sys import stdout
from os import path
import subprocess
import obrparser

# Checks if a key-value pair has an empty value
def isEmpty(value):
    if value == '':
        return True
    else:
        return False

# ### --- script begins here --- ###

# Relative path of OpenBusinessRepository
rawdata_path = input()

# Data processing
of_path = rawdata_path
# safeguard depending on how you obtain the
# data processing instruction file paths
if not path.exists(f_path):
    print("ERROR: DPI does not exist ->", f_path)
    exit(1)
# Parse .json file
try:
    with open(f_path) as f:
        data = json.load(f)
except ValueError: # failed parse
    print("ERROR: Failed to parse DPI ->", f_path)
    exit(1)
# These fields must exist and be non-empty in the format file!
try:
    if isEmpty(data['filename']) or \
       isEmpty(data['type']) or \
       isEmpty(data['info']['header']) or \
       isEmpty(data['info']['name']) or \
       isEmpty(data['info']['address']):
        print("ERROR: Contains an empty field ->", f_path)
        exit(1)
except KeyError: # semantic error
    print("ERROR: Missing required field ->", f_path)
    exit(1)

print("Acceptable syntax:", f_path)

if data['type'] == 'xml':
    es = obrparser.xml_parse(data)
    if es == 1:
        print("ERROR: Could not parse XML file ->", f_path)
    elif es == 2:
        print("ERROR: Could not find XML file in preprocessing ->", f_path)
elif data['type'] == 'csv':
    # handle unicode decoding errors before parsing

    es = obrparser.csv_parse(data)
    if es == 1:
        print("ERROR: Could not find CSV file in preprocessing ->", f_path)
    elif es == 2:
        print("ERROR: DPI fields and CSV column names disagree ->", f_path)
