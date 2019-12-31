.. _faq:

==========================
Frequently asked questions
==========================

-------------------------
What is the OpenTabulate?
-------------------------

OpenTabulate is an open source Python package developed by the Data Exploration and Integration Lab's (DEIL) at Statistics Canada. The goal is to provide a data processing framework to support DEIL's open data project, the *Linkable Open Data Environment* (LODE), where OpenTabulate plays the role of transforming data into a suitable format for record linkage. Our decided format to transform to is CSV (comma-separated values), hence the "Tabulate" in OpenTabulate.

----------------------------------------------------
What type of data content does OpenTabulate support?
----------------------------------------------------

OpenTabulate processes micro-level data (we simply call this *microdata*) such as contact information, addresses, geocoordinates, etc. of public facilities in Canada such as

* fire stations
* libraries
* hospitals
* education facilities (e.g. universities)
* businesses

As the project evolves, the list above will grow.

------------------------------------------------
What data formats can OpenTabulate process from?
------------------------------------------------

CSV and XML format are currently supported.

---------------------------
How do we use OpenTabulate?
---------------------------

Please view the `README <https://github.com/CSBP-CPSE/OpenTabulate>`_ and :ref:`running-opentabulate`.

---------------------------------
Why was the OpenTabulate written?
---------------------------------

After 2010, municipalities, provinces, federal departments and other organizations have started to release microdata as part of Canada's `open government initiative <https://open.canada.ca/en/about-open-government>`_. 

* is not released with a standardized schema shared among the participating groups
* is not consistently provided by each of the participating groups (although such information is public)
* is subject to copyright or some proprietary license

The LODE project aims to resolve the above to: process, link and distribute data under an `open government license <https://open.canada.ca/en/open-government-licence-canada>`_. OpenTabulate is a piece of the LODE project, providing a tool to reformat microdata to a standardized schema and format suitable for further processing.

-------------------------------------------------
What limitations are present in the OpenTabulate?
-------------------------------------------------

There are numerous features and code adjustments that can be made to improve OpenTabulate. The project altogther is relatively young and has a lot of room for growth and improvement. If you feel there is something missing, address it in our GitHub `issues <https://github.com/CSBP-CPSE/OpenBusinessRepository/issues>`_.

---------------------------------------
What is the future of the OpenTabulate?
---------------------------------------

There are a few development paths that are in consideration. An important one is to turn OpenTabulate into a general purpose tool. For example, we may allow for customized schemas to be defined in configuration files, instead of hard-coding, so just about any data content can be handled. Another path is to directly integrate the tool with the LODE, as it was originally intended for.
