# Frequently asked questions

#### What is the OBR?

The OpenBusinessRepository(OBR) is a software-based solution to one of DEIL's open data exploratory projects. Its purpose is to provide an open-source framework to integrate business microdata into a unified open database. Data are sourced from municipal, provincial, federal and other organizations that provide them under an open data license.

#### What type of data does OBR support?

Business register and business licensing microdata in CSV and XML format.

#### How do we use OBR?

Assuming you have completed the installation process, you:

- Write source files as described in `./docs/CONTRIB.md` (refer to the `sources` folder for examples) 
- Download the using OBR and the source file, or manually into `./pddir/raw/`
- Process the data using the script `$ python tools/obrpdctl.py PATH-TO-SOURCE-1 PATH-TO-SOURCE-2 ...`
- The processed files, which are in CSV format, are placed in `./pddir/clean`

#### Why was the OBR constructed?

Municipalities, provinces, federal departments and other organizations have started to release business microdata (registers, listings, etc.) with an open data license. This project is intended to explore the potential of these data sources for statistical purposes. In the future, this project could further contribute to the availability of open microdata by providing a unified and standardized database, distributed back to the public under an open data license.

#### What limitations are present in the OBR?

There are numerous features and code adjustments that have to be made to make OBR a more user-friendly program. The project altogther is relatively young and has a lot of room for growth and improvement. If you feel there is something missing, address it in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

#### What is the future of the OBR?

There are a variety of enhancements to be added and additional steps to take to further progress the OBR system. Writing and implementing good cleaning algorithms is a major part of our agenda and also to generalize the script to other types of data other than business data.
