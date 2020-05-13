# -*- coding: utf-8 -*-
"""
Unit tests for source file handling of OpenTabulate.

...

Created and written by Maksym Neyra-Nesterenko.

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""
import json
import os
import sys
import unittest

try:
    from opentabulate.source import Source
except ImportError:
    print("ERROR, could not import OpenTabulate API.", file=sys.stderr)
    exit(1)

class TestSourceParse(unittest.TestCase):
    """
    Source class unit tests to test functionality of parse().
    """
    def test(self):
        pass

if __name__ == '__main__':
    unittest.main()
