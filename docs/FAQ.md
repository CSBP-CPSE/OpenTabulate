# Frequently asked questions

#### What is the OBR?

The OpenBusinessRepository(OBR) is a software-based solution to one of DEIL's open data exploratory projects. Its purpose is to provide an open-source framework to integrate business microdata into a unified open database. Data are sourced from municipal, provincial, federal and other organizations that provide them under an open data license.

#### What type of data does OBR support?

Business register and business licensing microdata in CSV and XML format.

#### How do we use OBR?

Assuming you have completed the installation process, you:

- Write source files as described in `./docs/CONTRIB.md` (refer to the `sources` folder for examples) 
- If no `url` is provided for a source file, store the dataset in `./pddir/raw/`
- Run `$ python tools/pdctl.py PATH-TO-SOURCE-1 PATH-TO-SOURCE-2 ...`
- Resulting files are in `./pddir/clean`

#### Why was the OBR constructed?

Municipalities, provinces, federal departments and other organizations have started to release business microdata (registers, listings etc.) with an open data license. This project is intended to explore the potential of these data sources for statistical purposes. In the future, this project could further contribute to the availability of open microdata by providing a unified and standardized database, distributed back to the public under an open data license.

OBR is a small but core component of the exploratory project involving investigation of open data stemming from "authoritative" sources, such as public/private companies and provincial/municipal governments. By "open data", we refer to data accompanied with an open data license, which means the data is free to be distributed, claimed, and reused independent of the original source. Successful projects that pioneer the open data intiative, such as the Canadian civic address and building footprint databases, have given incentive to explore other types of data, such as business entity information. As a result, the OBR was made.

#### What limitations are present in the OBR?

The production system is currently not portable to Windows or Mac OS X. Besides that, the project is relatively young, it has a lot of room for growth and improvement. If you feel there is something missing, address it in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

#### What is the future of the OBR?

There are a variety of enhancements to be added and additional steps to take to further progress the production system. Further improvements to data cleaning and cleaning up the documentation and code is part of our agenda, to make the data more usable, to open up and make our project friendly for potential developer contribution. Business data is a stepping stone for Statistics Canada's open data initiative and our project is its own leap to modernize the public sector's approach to data analytics and to provide elegant solutions to problems in data science.
