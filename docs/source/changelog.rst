.. _changelog:

=========
Changelog
=========

Notable changes to OpenTabulate are listed below. This changelog format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ and follows `semantic versioning <https://semver.org/>`_.

.. _release-2.0.0:

..
  ------------
  [Unreleased]
  ------------

--------------------
[2.1.0] - 2020-07-08
--------------------

^^^^^
Added
^^^^^

- Multithreading support to allow parallelized processing of input data
- Caching using hash digests to avoid redundant data processing when invoking OpenTabulate more than once

^^^^^^^
Changed
^^^^^^^

- Improved error and logging messages
- Reorganized package contents n a code base, additional package data and unit tests
- Completed basic unit tests for ``algorithm.py``
 

--------------------
[2.0.0] - 2020-05-15
--------------------

^^^^^
Added
^^^^^

- Design specification
- Project changelog
- Configuration file with processing and output schema configuration

^^^^^^^
Changed
^^^^^^^

- Refactored code (renamed variables, relocated classes into files, removal of redundant code, implemented new functions)
- Ported Markdown documentation to ReST/Sphinx, now hosted `here <https://opentabulate.readthedocs.io/en/stable/>`_

^^^^^^^
Removed
^^^^^^^

- Downloading data from a URL
- ZIP file handling
- Address parsing
- Preprocessing and postprocessing script management


--------------------
[1.0.1] - 2019-04-29
--------------------

- *Added* a ``provider`` tag to source files to include and output a dataset identifier
- *Fixed* a bug where the ``XML_Algorithm`` class was meant to use ``csv.DictWriter`` instead of ``csv.writer``
  

--------------------
[1.0.0] - 2019-04-25
--------------------

- First release of OpenTabulate.
