# -*- coding: utf-8 -*-
"""
OpenTabulate is a Python package designed to organize, tabulate, and process 
structured data. It currently aims to be a data processing framework for the 
Linkable Open Data Environment, an exploratory project in development by the 
Data Exploration and Integration Lab (DEIL) at Statistics Canada. It primarily
offers

- a systematic way of organizing data using *sources files* (inspired by
  OpenAddresses),
- tabulation of data into a standardized CSV format that is suitable for merging 
  and linkage,
- basic data cleaning and formatting, data filtering and customizing output schema


Comprehensive documentation of OpenTabulate is linked here:

https://opentabulate.readthedocs.io/en/stable/index.html


In the 'main' module, consisting of the OpenTabulate code base, is broken down into
these parts:

- main.py             - command line tool (used as console script entry point)
- main_funcs.py       - wrapper functions for the command line tool
- args.py             - command line argument parsing and validation
- config.py           - configuration file parsing and validation
- cache.py            - cache manager class for avoiding redundant data processing
- source.py           - source file parsing and validation
- tabulate.py         - data processing wrappers
- algorithm.py        - data processing classes and methods
- thread.py           - multithreading pool for OpenTabulate
- thread_exception.py - exceptions for threading

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
