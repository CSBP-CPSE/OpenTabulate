"""
...

Written by Maksym Neyra-Nesterenko.
"""

from os import path

def check(SRC_JSON):
    # -- check with urls before proceeding --
    # ...
    # ...
    if not path.exists('./raw/' + SRC_JSON['file']):
        print("[E] 'file' not found in raw folder.")
        exit(1)

