============
Introduction
============

--------
Overview
--------

You may get a rough idea of what OpenTabulate is about in the `README <https://github.com/CSBP-CPSE/OpenTabulate>`_ and :ref:`FAQ <faq>`, but perhaps you want to know more. Specifically, OpenTabulate supports

* automated data retrieval
* a programmatic way of organizing and retrieving data using :ref:`sources files <source-files>` (inspired by `OpenAddresses <https://openaddress.io>`_),
* transform data to a standardized CSV format that is suitable for merging and linkage,
* various methods to process data, including address parsing and cleaning entries

OpenTabulate's API wrapper (written in ``tabulate.py``) defines a high-level ``DataProcess`` class, such that when its methods are strung together, forms a *processing pipeline*.

.. --%-- The content below must be updated to fit the new documentation! --%--
   
The processing pipeline can be described in four stages, each containing subroutines. The pipeline and its order of execution is summarized below, with *italicized* steps being *optional* (depending on the contents of a source file).

1. **Source file handling**
   
   a. Create a 'Source' object from a source file and parse it.
   b. *Download data from a URL.*
      
2. **Pre-processing**

   a. *Load an address parser.*
   b. Create a 'DataProcess' objects to wrap the processing steps.
   c. *Run pre-processing scripts on raw data.*
   d. Define schema transformation from 'Source' object.
   
3. **Standard processing**

   a. *If CSV with no specified encoding, predict encoding*
   b. Parse and tabulate data (regex filtering, basic entry cleaning, force values, etc.)
   c. Clean data (phone number entries, province names, etc.)

4. **Post-processing**

   a. *Run post-processing scripts on clean data*
   b. Store result in ``clean`` folder.


--------------------------------------
Key features
--------------------------------------

OpenTabulate supports several features that are useful in stringing together microdata, some of which are mentioned above. They are described them in detail below.

* **Downloading data.** The data can be referenced by a URL to be retrieved, using HTTP or FTP, and can come in a supported format even if compressed or archived.
* **Tabulation.** Convert data into CSV format with a common set of column names for easy merging.
* **Pre/post-processing scripts.** If OpenTabulate is missing a feature, you can fill in the gap by customizing and automating processing before and after OpenTabulate's tabulation and cleaning.
* **Regular expression filtering.** You can tabulate a subset of the data by regular expression filtering. All regular expressions must find a match in their corresponding attributes in order to mark the data entity for processing.
* **Basic cleaning and error filtering.** Easy data cleaning tasks (whitespace removal, unneeded punctuation, reformatting structured entries like phone numbers and postal codes) is handled by OpenTabulate. *Note that OpenTabulate does not perform imputation or attempt to predict the value of an ambigious entry*. Entries that could not be dealt with by OpenTabulate is filtered into an "error" file.
* **Address parsing support.** OpenTabulate can use `libpostal <https://github.com/openvenues/libpostal>`_ to parse addresses. To use it, the ``address_str_parse`` source file tag must be used. The tag specifies a full address string which libpostal will parse and split into tokens (such as street name, street number, postal code, etc.).

Other processing features are discussed in :ref:`source-files`.

To get started, see :ref:`running-opentabulate`.
