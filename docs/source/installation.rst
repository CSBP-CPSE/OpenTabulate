.. _installation:

============
Installation
============

------------------
Linux installation
------------------

To install the OpenTabulate package, one can use any tool that accesses the `Python Package Index <https://pypi.org>`_. In this guide, the command line tool ``pip`` is used to install OpenTabulate into a virtual environment in a recent version of Ubuntu or Debian Linux. Adapt and change the commands as needed.

^^^^^^^^^^^^
Requirements
^^^^^^^^^^^^

OpenTabulate runs in Python 3, from versions 3.5 and up. As long as your version of Python 3 is generally up-to-date, the package should operate. In Ubuntu or Debian, install the following packages using ``apt`` ::

  $ apt-get install python3 python3-venv python3-pip

if you do not have them already.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Setup and installing the package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create the virtual environment in whichever directory you prefer, then activate it. ::

  $ mkdir virtualenv
  $ python3 -m venv virtualenv
  $ source virtualenv/bin/activate
  (virtualenv) $

Now we can install OpenTabulate in our isolated virtual environment. ::

  (virtualenv) $ pip3 install opentabulate

Now OpenTabulate is ready to be ran with the ``opentab`` command. Note for future runs, the virtual environment must be activated to use the ``opentab`` command.

^^^^^^^^^^^^^^^^^^^^^^^^^
Initializing OpenTabulate
^^^^^^^^^^^^^^^^^^^^^^^^^

OpenTabulate has to be configured before it can be used. Copy the configuration file with ::

  (virtualenv) $ opentab --copy-config

This command copies the provided ``opentabulate.conf.example`` from the installed package to ``~/.config/opentabulate.conf``. Open the configuration file in a text editor and assign a path to a directory to the ``root_directory`` variable. Don't forget to remove the comment prefix for the variable!

Configuration (before): ::

  ...
  [general]
  ...
  #root_directory =
  ...

Configuration (after): ::

  ...
  [general]
  ...
  root_directory = /home/bob/opentabulate
  ...

Finally, initialize the OpenTabulate processing directories using ::

  (virtualenv) $ opentab --initialize

This completes the base installation to OpenTabulate. To get started using OpenTabulate, please read :ref: `Basic Usage <basic-usage>`.
