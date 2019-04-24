# -*- coding: utf-8 -*-
"""
Microdata processing, tabulation and cleaning support.

OpenTabulate is a Python package designed to organize, tabulate, and process 
structured data. It currently aims to be a data processing framework for the 
Linkable Open Data Environment, an exploratory project in development by the 
Data Exploration and Integration Lab (DEIL) at Statistics Canada. It offers

- automated data retrieval
- a systematic way of organizing and retrieving data using *sources files*
  (inspired by OpenAddresses),
- tabulation of data into a standardized CSV format that is suitable for merging 
  and linkage,
- various methods to process data, including address parsing, cleaning and 
  reformatting.

OpenTabulate's API defines several classes and methods, such that when put 
together form a *processing pipeline*. This simplifies the processing procedure 
as a sequence of class method invocations. Moreover, this design allows for ease 
of addition, modification and removal of code.


Created and written by Maksym Neyra-Nesterenko.

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""
