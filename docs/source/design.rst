.. _design:

====================
Design specification
====================

*This design specification holds as of OpenTabulate version 2.0. (last updated: 2020-04-27)*

This document details the design principles for OpenTabulate (OT). OT has served as a tool to tabulate structured data into a common format, complemented with tools such as data retrieval through the File Transfer Protocol (FTP) or Hypertext Transfer Protocol (HTTP), address parsing and simple data cleaning. The project has evolved to suit the needs of the Data Exploration and Integration Lab (DEIL) at Statistics Canada, and one of our major goals is to neatly organize our data processing framework. As a result, this design specification was born. This is not an instruction manual but rather an informal guide to implementing OpenTabulate. This is summarized in the sections below.

----------
Modularity
----------

OT will be modular in sense of both code and configuration. The implementation of OT should make it easy to add or discard components while fulfilling backwards compatibility. Mappings of schemas and other functionality such as logging and data cleaning will be specified by the end-user in a configuration file.

----------
Tabulation
----------

*OT will focus on adhering to its designated (main) purpose, tabulating structured data*. By structured, it is emphasized that the input data is assumed to be well-formed and should interrupt processing if it finds that the input data structure is not well-formed. By well-formed, we mean that the input should be valid and follow the standards of the data format. For example, CSV files should adhere to `RFC 4180 <https://tools.ietf.org/html/rfc4180>`_ and XML files should adhere to `W3's specification <https://www.w3.org/TR/xml/>`_.

OT can support other functionality provided it does not stray away from its main purpose. For example, it can

* Clean input entries independent of data type or content (e.g. removal of whitespace)
* Divide a data entry into multiple entries
* Drop entities (e.g. entire CSV rows) based on a string filtering criteria

but it should not

* Validate or correct data content (e.g. is a postal code entry well-formed?)
* Data entries that are kept should not have content dropped or altered in a way that does not make it semantically equivalent to the original data

If OT creates new columns based on the existing data contents, the content used should be tabulated to the output instead of being discarded.

----------
Minimality
----------

OT must be simple in its design. If there is desired functionality in a data processing framework not served by OT, that functionality should be excluded from OT. External tools must instead be used for the end user's data processing framework.
