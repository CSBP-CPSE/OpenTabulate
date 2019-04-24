# Frequently asked questions

#### What is the OpenTabulate?

OpenTabulate is a Python package developed by the Data Exploration and Integration Lab's (DEIL) at Statistics Canada. The goal is to provide a data processing framework to support DEIL's open data project, Linkable Open Data Environment (LODE), where OpenTabulate acts as a precursor to record linkage by assembling **microdata** into unified and tabular databases.

By microdata, we refer to information captured at an establishment level, such as contact and location information of fire stations, businesses, education facilities, and so on. 

#### What type of data content does OpenTabulate support?

OpenTabulate is currently set up to focus on (but is not limited to) contact and location data of establishments, such as

- fire stations
- libraries
- hospitals
- education facilities
- businesses

Given the structure of the code, it is easy to integrate more categories of establishments and data attributes if needed.

#### What data formats can OpenTabulate process from?

Raw data in CSV and XML format are currently supported.

#### How do we use OpenTabulate?

Please view the [README](/README.md) and [Running OpenTabulate](running_opentab.md).

#### Why was the OpenTabulate written?

Municipalities, provinces, federal departments and other organizations have started to release microdata (business registers, education facilities, etc.) but in a non-standardized fashion. The goal is to 

- reformat the data in a standardized format suitable for record linkage
- redistribute the processed or linked form under an open data license

#### What limitations are present in the OpenTabulate?

There are numerous features and code adjustments that can be made to improve OpenTabulate. The project altogther is relatively young and has a lot of room for growth and improvement. If you feel there is something missing, address it in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

#### What is the future of the OpenTabulate?

There are a few development paths that are in consideration. An important one is to turn OpenTabulate into a general purpose tool. For example, we may migrate establishment categories and data attributes into configuration files, instead of hard-coding, so just about any data content can be handled. Another path is integrate the tool with the Linkable Open Data Environment (LODE), as it was originally intended for.
