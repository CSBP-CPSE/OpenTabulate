# Frequently asked questions

#### What is the OBR?

OBR (an abbreviation of OpenBusinessRepository) is a software-based solution to one of many projects attributing to Statistics Canada's open data initiative. Its purpose is to provide an open-source framework to integrate business data from Canadian municipalities and organizations that possess an open data license into a unified public database.

#### What type of data does OBR support?

Business register and licensing data in CSV and XML format.

#### How do we use OBR?

Assuming you have completed the installation process, you:

- Write source files as described in `./docs/CONTRIB.md` (refer to the `sources` folder for examples) 
- If no `url` is provided for a source file, store the dataset in `./pddir/raw/`
- Run `$ python tools/pdctl.py PATH-TO-SOURCE-1 PATH-TO-SOURCE-2 ...`
- Resulting files are in `./pddir/clean`

#### Why was the OBR constructed?

To give background, most business data used for statistical analysis at Statistics Canada is obtained from surveys and administrative sources. Some of these administrative sources have or recently began releasing open data for businesses, and Statistics Canada can take advantage of this by being able to validate the information. Additionally, Statistics Canada can further contribute to the open data community by getting involved with unifying the data via processing and standardization, in order for it to be distributed back to the public for free use under the open data license.

OBR is a small but core component of the exploratory project involving investigation of open data stemming from "authoritative" sources, such as public/private companies and provincial/municipal governments. By "open data", we refer to data accompanied with an open data license, which means the data is free to be distributed, claimed, and reused independent of the original source. Successful projects that pioneer the open data intiative, such as the Canadian civic address and building footprint databases, have given incentive to explore other types of data, such as business entity information. As a result, the OBR was made.

#### What limitations are present in the OBR?

The production system is currently not portable to Windows or Mac OS X. Besides that, the project is relatively young, it has a lot of room for growth and improvement. If you feel there is something missing, address it in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

#### What is the future of the OBR?

There are a variety of enhancements to be added and additional steps to take to further progress the production system. Further improvements to data cleaning and cleaning up the documentation and code is part of our agenda, to make the data more usable, to open up and make our project friendly for potential developer contribution. Business data is a stepping stone for Statistics Canada's open data initiative and our project is its own leap to modernize the public sector's approach to data analytics and to provide elegant solutions to problems in data science.
