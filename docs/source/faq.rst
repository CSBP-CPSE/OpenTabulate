.. _faq:

==========================
Frequently asked questions
==========================

^^^^^^^^^^^^^^^^^^^^^
What is OpenTabulate?
^^^^^^^^^^^^^^^^^^^^^

OpenTabulate is an open source Python package developed by the Data Exploration and Integration Lab's (DEIL) at Statistics Canada. The goal is to provide a data processing framework to support DEIL's open data project, the *Linkable Open Data Environment* (LODE), where OpenTabulate plays the role of transforming data into a suitable format for record linkage. Our decided format to transform to is CSV (comma-separated values), hence the "Tabulate" in OpenTabulate.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
What kind of data can OpenTabulate process?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenTabulate can process text data when it is in well-formed CSV or XML format.

^^^^^^^^^^^^^^^^^^^^^^^^^^^
How do we use OpenTabulate?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please view these parts of the documentation: :ref:`installation` and :ref:`basic-usage`.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Why was the OpenTabulate written?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After 2010, municipalities, provinces, federal departments and other organizations have started to release microdata as part of Canada's `open government initiative <https://open.canada.ca/en/about-open-government>`_. 

* is not released with a standardized schema shared among the participating groups
* is not consistently provided by each of the participating groups (although such information is public)
* is subject to copyright or some proprietary license

The LODE project aims to resolve the above to: process, link and distribute data under an `open government license <https://open.canada.ca/en/open-government-licence-canada>`_. OpenTabulate is a small component of the LODE project, which organizes our microdata and automates tabulating it to our standardized schema for further processing.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
What limitations are present in the OpenTabulate?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A good place to undestand the limitations of OpenTabulate are in our design specification (it's a short read). The project is young, there are numerous features and code adjustments that can be made to improve OpenTabulate, but it must adhere to the aforementioned specification.

If you feel there is something missing, let us know on `Github <https://github.com/CSBP-CPSE/OpenTabulate/issues>`_.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
What is the future of the OpenTabulate?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At this stage, OpenTabulate is fulfilling its purpose for DEIL. Bug fixes and minor updates will certainly come around, but no significant changes to the code base.

