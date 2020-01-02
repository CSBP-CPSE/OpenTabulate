.. _running-opentabulate:

====================
Running OpenTabulate
====================

------------------------
Directory initialization
------------------------

The command-line tool ``opentab`` is shipped with OpenTabulate after installation with ``pip``. It is a tool used to manage the data processing framework that OpenTabulate models. If you have not done so already, run::

  $ opentab --initialize DATA_DIR

where ``DATA_DIR`` is a (preferably empty) directory. This initializes OpenTabulate's workspace, which is defined in ::

  ~/.config/opentabulate.conf

The ``--initialize`` flag creates a set of directories::

  DATA_DIR/
  - data/
     - raw/
     - pre/
     - dirty/
     - clean/
  - sources/
  - scripts/

The directories under ``data`` are data processing directories, each described in the table below. Additionally, the ``sources`` and ``scripts`` are not necessary, but they are added as a default place to organize source and script files.

+-----------+-----------------------------------------------------------------------------------+
| Directory | Description                                                                       |
+===========+===================================================================================+
| ``raw``   | Source datasets should be stored here, noting that if your dataset is specified   |
|           | by ``url`` in a source file, it will be downloaded to this directory.             |
+-----------+-----------------------------------------------------------------------------------+
| ``pre``   | Datasets flagged for pre-processing are sent here from ``raw``.                   |
+-----------+-----------------------------------------------------------------------------------+
| ``dirty`` | Datasets from ``raw`` or ``pre`` are sent here during processing. They represent  |
|           | datasets converted to CSV format that have not been cleaned yet.                  |
+-----------+-----------------------------------------------------------------------------------+
| ``clean`` | Datasets are sent here after cleaning.                                            |
+-----------+-----------------------------------------------------------------------------------+

------------------
Command-line usage
------------------

For general usage, the form is::

  opentab [optional arguments] [SOURCE [SOURCE ...]]

``SOURCE`` is the path of a :ref:`source file<source-files>` corresponds to the data to be processed. Multiple source file paths can be included to process in the same command. Remember that the data associated with a source file must placed in the ``raw`` folder if a ``url`` key is not present in the source file! Optional command-line arguments are listed in the table below.


+------------+----------------------+-----------------------------------------------------------+
| Short flag | Long flag            | Description                                               |
+============+======================+===========================================================+
| ``-h``     | ``--help``           | Print the command-line tool help prompt to standard       |
|            |                      | output.                                                   |
+------------+----------------------+-----------------------------------------------------------+
| ``-p``     | ``--no-process``     | Do not process the datasets corresponding the source file.|
|            |                      | Useful for quickly checking source file syntax.           |
+------------+----------------------+-----------------------------------------------------------+
| ``-u``     | ``--download-url``   | From every source file which has a ``url`` key present,   |
|            |                      | download the data specified by the ``url`` value.         |
+------------+----------------------+-----------------------------------------------------------+
| ``-j N``   | ``--jobs N``         | Run asynchronous data processing jobs, where at most *N*  |
|            |                      | processes can simultaneously be running. *N* must be a    |
|            |                      | positive integer.                                         |
+------------+----------------------+-----------------------------------------------------------+
|            | ``--initialize DIR`` | Create the data processing directories used by            |
|            |                      | OpenTabulate in ``DIR``.                                  |
+------------+----------------------+-----------------------------------------------------------+
|            | ``--pre``            | Allow execution of pre-processing scripts from ``pre``    |
|            |                      | keys.                                                     |
+------------+----------------------+-----------------------------------------------------------+
|            | ``--post``           | Allow execution of post-processing scripts from ``post``  |
|            |                      | keys.                                                     |
+------------+----------------------+-----------------------------------------------------------+

The command line usage information can be printed in a terminal by entering::

  $ opentab --help

-----------
Example use
-----------

For the examples below, the current working directory is the configured OpenTabulate directory ``DATA_DIR`` and we have source files ``SOURCE1.json`` and ``SOURCE2.json`` stored in ``sources`` in the initialized OpenTabulate directory.

Basic use: ::

  $ opentab sources/SOURCE1.json

Run ``opentab`` using two CPU cores for processing and download data from URLs: ::

  $ opentab -j 2 -u sources/SOURCE1.json sources/SOURCE2.json

Check syntax for source file: ::

  $ opentab --no-process sources/SOURCE1.json
