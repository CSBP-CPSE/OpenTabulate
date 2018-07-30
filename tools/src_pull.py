"""
...

Written by Maksym Neyra-Nesterenko.
"""

from os import path

import src_fetch_url

def pull(SRC_JSON, INTERNET_FLAG):
    if ('url' in SRC_JSON) and INTERNET_FLAG == 1:
        src_fetch_url.fetch_url(SRC_JSON['url'], SRC_JSON['file'])
    if not path.exists('./raw/' + SRC_JSON['file']):
        print("[E] '", SRC_JSON['file'], "' not found in raw folder.", sep='')
        exit(1)
    
