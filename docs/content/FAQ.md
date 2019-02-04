# Frequently asked questions

#### What is the OpenTabulate?

OpenTabulate is a software-based solution to one of DEIL's open data exploratory projects. Its purpose is to provide an open-source framework to integrate microdata into a unified open database.

#### What type of data does OpenTabulate support?

For now, just about any microdata in CSV and XML format that has contact and location information. 

#### How do we use OpenTabulate?

1. Clone the OpenTabulate repository
2. [Write source files](CONTRIB.md) 
3. Familiarize yourself with the easy to use [command-line tool](RUN_OPENTAB.mb) `tabctl.py`
4. Download the using OBR and the source file, or manually into `pddir/raw`
5. Process the data using `tabctl.py`

For more details, refer to the user-friendly documentation provided [here](/docs/WELCOME.md).

#### Why was the OpenTabulate written?

Municipalities, provinces, federal departments and other organizations have started to release microdata (business registers, education facilities, etc.) but in a non-standardized fashion. The goal is to reformat the data in a standardized format to put together and redistribute.

#### What limitations are present in the OpenTabulate?

There are numerous features and code adjustments that have to be made to make OpenTabulate a more user-friendly program. The project altogther is relatively young and has a lot of room for growth and improvement. If you feel there is something missing, address it in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

#### What is the future of the OpenTabulate?

The project will look to merge with another exploratory project involving data linkage, so as to provide a data standardization, tabulation, and linkage system for open data.
