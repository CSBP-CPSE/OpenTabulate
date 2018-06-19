"""
A data processing tool for OpenBusinessRepository.

This module serves to handle problematic CSV data, i.e. those that are not written in the UTF-8
character encoding. Since this is data is Canadian, data files that fail to be decoded from
UTF-8 are assumed to use the CF863 encoding (a legacy MS-DOS French character encoding) and are 
converted to UTF-8. 

Written by Maksym Neyra-Nesterenko.
"""

import csv

def test_UTF8(path_to_file):
    source_dataset = open(path_to_file, 'r', encoding='utf-8', newline='')
    reader = csv.reader(source_dataset)
    count = 1
    try:
        for row in reader:
            count = count + 1
            str(row)
    except UnicodeDecodeError:
        return False, count
    
    return True

path = input()
print(path, test_UTF8(path))

