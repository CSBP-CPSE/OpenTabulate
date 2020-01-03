.. _changelog:

=========
Changelog
=========

Notable changes to OpenTabulate are listed below. This changelog format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ and follows `semantic versioning <https://semver.org/>`_.

.. _release-2.0.0:

--------------------
[2.0.0] - 2020-01-03
--------------------

^^^^^
Added
^^^^^

- Project changelog
- OpenTabulate configuration file 
- Address tag that stores the full address without address parsing
- (Incomplete) set of unit tests

^^^^^^^
Changed
^^^^^^^

- Refactored code (renamed variables, relocated classes into files,
  removal of redundant code, implemented new functions)
- Renamed source file keys to improve human readability, some have been **deprecated** or **removed**.
- Altered OpenTabulate ``--initialize``  flag to support new configuration file
- Ported Markdown documentation to ReST/Sphinx, now hosted `here <https://opentabulate.readthedocs.io/en/latest/>`_

^^^^^^^
Removed
^^^^^^^

- ZIP file handling

--------------------
[1.0.1] - 2019-04-29
--------------------

- *Added* a ``provider`` tag to source files to include and output a dataset identifier
- *Fixed* a bug where the ``XML_Algorithm`` class was meant to use ``csv.DictWriter`` instead of ``csv.writer``
  

--------------------
[1.0.0] - 2019-04-25
--------------------

- First release of OpenTabulate.
