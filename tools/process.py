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
import obrparser

# Checks if a key-value pair has an empty value
def isEmpty(value):
    if value == '':
        return True
    else:
        return False

# ### --- script begins here --- ###

# Relative path of OpenBusinessRepository
obr_p_path = input()

# Relative path of format file
FORMAT_REL_P_LIST = stdin.readlines()

# Data processing
for f_path in FORMAT_REL_P_LIST:
    f_path = f_path[:-1]
    # safeguard depending on how you obtain the
    # data processing instruction file paths
    if not path.exists(f_path):
        print("File does not exist ->", f_path)
        continue
    # Parse .json file
    try:
        with open(f_path) as f:
            data = json.load(f)
    except ValueError: # failed parse
        print("Failed to parse ->", f_path)
        continue
    # These fields must exist and be non-empty in the format file!
    try:
        if isEmpty(data['filename']) or \
           isEmpty(data['type']) or \
           isEmpty(data['info']['header']) or \
           isEmpty(data['info']['name']) or \
           isEmpty(data['info']['address']):
            print("Contains an empty field ->", f_path)
            continue
    except KeyError: # semantic error
        print("Missing required field ->", f_path)
        continue
    print("PASSED:", f_path)
    # %%% alert %%% : see parser.py
    if data['type'] == 'xml':
        obrparser.xml_parse(data,obr_p_path)
    elif data['type'] == 'csv':
        obrparser.csv_parse(data,obr_p_path)
