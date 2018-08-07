"""
...

Written by Maksym Neyra-Nesterenko.
"""

import json
import urllib.request
from os import path

import data_parser


def parse(SRC_PATH, NO_INTERNET_FLAG):
    print("[ ] Parsing source file :", SRC_PATH)
    if not path.exists(SRC_PATH):
        print("[E] Input path does not exist.")
        return None

    # parse .json file
    try:
        with open(SRC_PATH) as f:
            data = json.load(f)
    except ValueError: # failed parse
        print("[E] Incorrect JSON format.")
        return None

    # required tags
    if ('format' not in data) or ('file' not in data) or ('info' not in data):
        print("[E] At least one of 'format', 'file', 'info' is missing.")
        return None
    else:
        if (not isinstance(data['format'], str)) or \
           (not isinstance(data['file'], str)) or \
           (not isinstance(data['info'], dict)):
            print("[E] At least one of 'format', 'file', or 'info' is the wrong JSON type.")
            return None

    # required formats
    if (data['format'] != 'xml') and (data['format'] != 'csv'):
        print("[E] Unsupported data format '", data['format'],"'", sep='')
        return None

    # required header if format is not csv
    if data['format'] != 'csv' and ('header' not in data):
        print("[E] Format", data['format'], " requires 'header' tag.")
        return None

    if (data['format'] != 'csv') and ('header' in data) and (not isinstance(data['header'], str)):
        print("[E] 'header' must be a JSON string")
        return None

    # url
    if 'url' in data and (not isinstance(data['url'], str)):
        print("[E] 'url' must be a JSON string.")
        return None
            
    # check that both full_addr and address are not in the source file
    if ('address' in data['info']) and ('full_addr' in data['info']):
        print("[E] Cannot have both 'full_addr' and 'address' tags in source file.")
        return None

    # verify address is an object with valid tags
    if 'address' in data['info']:
        if not (isinstance(data['info']['address'], dict)):
            print("[E] Address tag is not a JSON object.")
            return None
        for i in data['info']['address']:
            if not (i in data_parser.ADDR_FIELD_LABEL):
                print("[E] Address tag contains an invalid key.")
                return None

    # verify force is an object with valid tags
    if 'force' in data:
        if not (isinstance(data['force'], dict)):
            print("[E] Force tag is not a JSON object.")
            return None
        for i in data['force']:
            if not (i in data_parser.FORCE_LABEL):
                print("[E] Force tag contains an invalid key.")
                return None
            elif ('address' in data['info']) and (i in data['info']['address']):
                print("[E] The key '", i, "' appears in 'force' and 'address'.")
                return None

    print("[!] Source file parsing suggests nothing blatantly out of the ordinary.")

    if ('url' in data) and NO_INTERNET_FLAG == False:
        _fetch_url(data['url'], data['file'])
    if not path.exists('./pddir/raw/' + data['file']):
        print("[E] '", data['file'], "' not found in raw folder.", sep='')
        return None
    return data



def _fetch_url(URL, FILENAME):
    try:
        response = urllib.request.urlopen(URL)
        data = response.read()
    except:
        print("[W] fetch_url failed, attempting fallback 'file'.")
        return
    # if the exception was not caught, proceed to write
    fw = open('./pddir/raw/' + FILENAME, 'wb')
    fw.write(data)
    fw.close()
