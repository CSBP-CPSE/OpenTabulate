"""
...

Written by Maksym Neyra-Nesterenko.
"""

import json
from os import path

import data_parser


def parse(SRC_PATH):
    print("[ ] Parsing source file :", SRC_PATH)
    if not path.exists(SRC_PATH):
        print("[E] Input path does exist.")
        exit(1)

    # parse .json file
    try:
        with open(SRC_PATH) as f:
            data = json.load(f)
    except ValueError: # failed parse
        print("[E] Incorrect JSON format.")
        exit(1)

    # required tags
    if ('format' not in data) or ('file' not in data) or ('info' not in data):
        print("[E] At least one of 'format', 'file', 'info' is missing.")
        exit(1)

    # required formats
    if (data['format'] != 'xml') and (data['format'] != 'csv'):
        print("[E] Unsupported data format '", data['format'],"'", sep='')
        exit(1)

    # required header if format is not csv
    if data['format'] != 'csv' and ('header' not in data):
        print("[E] Format", data['format'], " requires 'header' tag.")
        exit(1)

    # verify address is an object with valid tags
    if 'address' in data['info']:
        if not (isinstance(data['info']['address'], dict)):
            print("[E] Address tag is not a JSON object.")
            exit(1)
        for i in data['info']['address']:
            if not (i in data_parser.ADDR_FIELD_LABEL):
                print("[E] Address tag contains an invalid key.")
                exit(1)

    # verify force is an object with valid tags
    if 'force' in data:
        if not (isinstance(data['force'], dict)):
            print("[E] Force tag is not a JSON object.")
            exit(1)
        for i in data['force']:
            if not (i in data_parser.FORCE_LABEL):
                print("[E] Force tag contains an invalid key.")
                exit(1)
            elif ('address' in data['info']) and (i in data['info']['address']):
                print("[E] The key '", i, "' appears in 'force' and 'address'.")
                exit(1)

    print("[!] Source file parsing suggests nothing blatantly out of the ordinary.")
    return data
