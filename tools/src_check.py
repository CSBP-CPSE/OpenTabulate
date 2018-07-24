"""
...

Written by Maksym Neyra-Nesterenko.
"""

from os import path

import src_fetch_url

def check(SRC_JSON):
    if 'url' in SRC_JSON:
        src_fetch_url.fetch_url(SRC_JSON['url'], SRC_JSON['file'])
    if not path.exists('./raw/' + SRC_JSON['file']):
        print("[E] '", SRC_JSON['file'], "' not found in raw folder.", sep='')
        exit(1)
    
