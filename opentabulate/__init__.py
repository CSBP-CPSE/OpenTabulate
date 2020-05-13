# -*- coding: utf-8 -*-
"""
OpenTabulate is a Python package designed to organize, tabulate, and process 
structured data. It currently aims to be a data processing framework for the 
Linkable Open Data Environment, an exploratory project in development by the 
Data Exploration and Integration Lab (DEIL) at Statistics Canada. It primarily
offers

- a systematic way of organizing and retrieving data using *sources files*
  (inspired by OpenAddresses),
- tabulation of data into a standardized CSV format that is suitable for merging 
  and linkage,
- basic data cleaning and formatting, data filtering and customizing output schema


Comprehensive documentation of OpenTabulate is linked here:

https://opentabulate.readthedocs.io/en/stable/index.html


To review the code, the package is broken down into these parts:

- opentab.py : command line tool
- opentab_funcs.py : wrapper functions for the command line tool
- args.py : command line argument parsing and validation
- config.py : configuration file parsing and validation
- source.py : source file parsing and validation
- tabulate.py : data processing wrappers
- algorithm.py: data processing classes and methods

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
