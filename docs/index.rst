.. OpenTabulate documentation master file, created by
   sphinx-quickstart on Wed Nov 13 21:01:56 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenTabulate's documentation!
========================================

OpenTabulate is an open source Python package developed by the Data Exploration and Integration Lab (DEIL) at Statistics Canada. Its original use was for DEIL's *Linkable Open Data Environment* (LODE) project, but has evolved since then. OpenTabulate provides the following core features:

* a programmatic way of organizing processing and data using :ref:`sources files <source-files>` (inspired by `OpenAddresses <https://openaddress.io>`_),
* transforms data to a standardized CSV format that is suitable for merging,
* configurable settings that apply simple cleanup and standardization to the data.

OpenTabulate is meant to be a :ref:`simple tool <design>`, one that complements a data processing pipeline. To get started, please see :ref:`Installation <installation>` and :ref:`Basic Usage <basic-usage>`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/installation
   source/basic-usage
   source/configuration
   source/command-args
   source/source-files
   source/faq
   source/design
   source/changelog
   

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

