# -*- coding: utf-8 -*-
"""
Source file API.

This module holds the Source class for OpenTabulate, which is an object that stores
metadata about the datasets to be processed by OpenTabulate. The metadata is extracted
during initialization of the object, which reads a corresponding "source file" 
formatted in JSON.

The Source object is designed to be mutable and is modified by DataProcess objects 
to abstract the data processing.


Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""

# Code comment prefixes: 
# IMPORTANT, SUGGESTION, DEBUG, TESTING, DEPRECATED
# ---

###########
# MODULES #
###########

import json
import logging
import os
import re
import requests
import urllib.request as req

#############
# VARIABLES #
#############

# -- JSON tags --

#
# SUGGESTION: have shared or immutable 'global' variables for source objects
# 

#################################
# SOURCE DATASET METADATA CLASS #
#################################

class Source(object):
    """
    Source dataset class. Abstracts a dataset by storing metadata involving the data 
    file (format, name, etc.) and structure (XML headers, CSV delimiter, schema, etc.). 
    Other processing metadata inferred from a source file (file paths, scripts, etc.)
    used by OpenTabulate are also stored.

    Attributes:
        srcpath (str): Source file path.
        metadata (dict): Source file JSON dumps.

        default_paths (bool): Allow Source.parse() to assign default paths to
            the path attributes described below
        has_pre (bool): pre-process flag
        has_post (bool): post-process flag
        download_url (bool): download data flag
        
        localfile (str): Data file name (not path).
        rawpath (str): Raw data path (in './data/raw/').
        prepath (str): Preprocessed data path (in './data/raw/')
        prepath_temp (str): Temporary file (in './data/raw/')
        
        dirtypath (str): Dirty tabulated data path (in './data/dirty/').
        cleanpath (str): Clean tabulated data path (in './data/clean/').
        dirtyerror (str): ---
        cleanerror (str): Data that could not be tabulated (in './data/clean/')
        

        label_map (dict): Mapping of standardized labels (in Algorithm) to
            the raw datasets labels, obtained from self.metadata.
        log (Logger): Logger with self.localfile as its name.
    """
    def __init__(self, path,
                 has_pre=False, has_post=False,
                 download_url=False, default_paths=True):
        """
        Initializes a new source file object.

        Raises:
            OSError: Path (of source file) does not exist.
        """
        if not os.path.exists(path):
            raise OSError('Path "%s" does not exist.' % path)
        self.srcpath = path
        with open(path) as f:
            self.metadata = json.load(f)

        # used separately for debugging and unit test writing
        #
        # SUGGESTION: Add warnings if path variables are set to None?
        self.default_paths = default_paths
        
        # flags -- determined by command line arguments
        self.has_pre = has_pre
        self.has_post = has_post
        self.download_url = download_url
        
        # processing path variables -- determined during parsing
        self.localfile = None
        self.rawpath = None
        self.prepath = None
        self.prepath_temp = None
        self.dirtypath = None
        self.cleanpath = None
        self.dirtyerror = None # DEPRECATED (for now)
        self.cleanerror = None
        
        self.label_map = None

        self.logger = None

        
    def parse(self):
        """
        Parses the source file to check correction of syntax.

        Raises:
            LookupError: Missing tag.
            ValueError: Incorrect entry or combination or entries, such as having
                an 'address_tokens' and 'address_str_parse' tag will raise this error since they 
                cannot both be used in a source file.
            TypeError: Incorrect JSON type for a tag.
            OSError: Path for pre or post processing scripts not found.
        """

        print("Parsing", self.srcpath)
        
        src_str = os.path.basename(self.srcpath)
        # SUGGESTION: replace Python error handling (and use logging)?
        #parse_log = logging.getLogger(name=srcpath)
        #parse_log.info("Parsing", self.srcpath)

        self._convert_backward_compat_keys()
        
        #####################
        # REQUIRED METADATA #
        #####################

        # first set of required tags
        first_req_tags = ('localfile', 'format', 'schema', 'database_type')
        for tag in first_req_tags:
            if tag not in self.metadata:
                raise LookupError("%s '%s' tag is missing." % (src_str, tag))
            
        # types required for required tags
        if not isinstance(self.metadata['localfile'], str):
            raise TypeError("%s 'localfile' must be a string." % src_str)
        if not isinstance(self.metadata['format'], dict):
            raise TypeError("%s 'format' must be an object." % src_str)
        if not isinstance(self.metadata['schema'], dict):
            raise TypeError("%s 'schema' must be an object." % src_str)
        if not isinstance(self.metadata['database_type'], str):
            raise TypeError("%s 'database_type' must be a string." % src_str)

        # required database types
        db_types = ('business', 'hospital', 'library', 'fire_station', 'education')
        if self.metadata['database_type'] not in db_types:
            raise ValueError("%s Unsupported database type '%s'" % (src_str, self.metadata['database_type']))

        # required tags for 'format'
        if 'type' not in self.metadata['format']:
            raise LookupError("%s 'format.type' tag is missing." % src_str)
        if not isinstance(self.metadata['format']['type'], str):
            raise TypeError("%s 'format.type' must be a string." % src_str)

        # required formats
        if (self.metadata['format']['type'] == 'csv'):
            # -- CSV --
            # delimiter
            if 'delimiter' not in self.metadata['format']:
                raise LookupError("%s 'format.delimiter' tag is missing for format 'csv'" % src_str)
            elif not (isinstance(self.metadata['format']['delimiter'], str) and
                      len(self.metadata['format']['delimiter']) == 1):
                raise TypeError("%s 'format.delimiter' must be a single character string." % src_str)
            
            # quotes
            if 'quote' not in self.metadata['format']:
                raise LookupError("%s 'format.quote' tag is missing for format 'csv'" % src_str)
            elif not (isinstance(self.metadata['format']['quote'], str) and
                      len(self.metadata['format']['quote']) == 1):
                raise TypeError("%s 'format.quote' must be a single character string." % src_str)
            
        elif (self.metadata['format']['type'] == 'xml'):
            # -- XML --
            # xml header
            if 'header' not in self.metadata['format']:
                raise LookupError("%s 'format.header' tag is missing for format 'xml'" % src_str)
            elif not isinstance(self.metadata['format']['header'], str):
                raise TypeError("%s 'format.header' must be a string." % src_str)
        else:
            # -- unsupported format --
            raise ValueError("%s Unsupported data format '%s'" % (src_str, self.metadata['format']['type']))
        
        #####################
        # OPTIONAL METADATA #
        #####################

        # dataset provider (name)
        if 'provider' in self.metadata and (not isinstance(self.metadata['provider'], str)):
            raise TypeError("%s 'provider' must be a string." % src_str)

        # url
        if 'url' in self.metadata and (not isinstance(self.metadata['url'], str)):
            raise TypeError("%s 'url' must be a string." % src_str)

        '''
        # DEPRECATED #
        
        # compression
        if 'compression' in self.metadata:
            if not isinstance(self.metadata['compression'], str):
                raise TypeError(where_str + "'compression' must be a string.")
            if self.metadata['compression'] != 'zip':
                raise ValueError(where_str + "Unsupported compression format '" + self.metadata['compression'] + "'")
        

        # localarchive
        if ('localarchive' in self.metadata) and ('compression' not in self.metadata):
            raise LookupError(where_str + "'compression' tag missing for localarchive " + self.metadata['localarchive'])
        '''

        # -- preprocessing type and path existence check --
        if 'pre' in self.metadata:
            if not (isinstance(self.metadata['pre'], str) or isinstance(self.metadata['pre'], list)):
                raise TypeError(where_str + "'pre' must be a string or a list of strings.")

            if isinstance(self.metadata['pre'], list):
                for entry in self.metadata['pre']:
                    if not isinstance(entry, str):
                        raise TypeError(where_str + "'pre' must be a string or a list of strings.")

            if isinstance(self.metadata['pre'], str) and not os.path.exists(self.metadata['pre']):
                raise OSError(where_str + 'Preprocessing script "%s" does not exist.' % self.metadata['pre'])
            elif isinstance(self.metadata['pre'], list):
                for script_path in self.metadata['pre']:
                    if not os.path.exists(script_path):
                        raise OSError(where_str + 'Preprocessing script "%s" does not exist.' % script_path)

        # -- postprocessing type and path existence check --
        if 'post' in self.metadata:
            if not (isinstance(self.metadata['post'], str) or isinstance(self.metadata['post'], list)):
                raise TypeError(where_str + "'post' must be a string or a list of strings.")

            if isinstance(self.metadata['post'], list):
                for entry in self.metadata['post']:
                    if not isinstance(entry, str):
                        raise TypeError(where_str + "'post' must be a string or a list of strings.")

            if isinstance(self.metadata['post'], str) and not os.path.exists(self.metadata['post']):
                raise OSError(where_str + 'Postprocessing script "%s" does not exist.' % self.metadata['post'])
            elif isinstance(self.metadata['post'], list):
                for script_path in self.metadata['post']:
                    if not os.path.exists(script_path):
                        raise OSError(where_str + 'Postprocessing script "%s" does not exist.' % script_path)                    
        # -- filter contents check --
        if 'filter' in self.metadata:
            if not isinstance(self.metadata['filter'], dict):
                raise TypeError("%s 'filter' must be an object." % src_str)
            else:
                for attribute in self.metadata['filter']:
                    if not isinstance(self.metadata['filter'][attribute], str):
                        raise TypeError("%s Filter attribute '%s' must be a string (regex)." % (src_str, attribute))
                    else:
                        attr_filter = self.metadata['filter'][attribute]
                        regexp = re.compile(attr_filter)
                        self.metadata['filter'][attribute] = regexp


        # check that both address_str_parse and address_tokens are not in the source file
        if ('address_tokens' in self.metadata['schema']) and ('address_str_parse' in self.metadata['schema']):
            raise ValueError(
                "%s Cannot have both 'schema.address_str_parse' and 'schema.address_tokens' tags." % src_str
            )

        # verify address_tokens is an object
        if 'address_tokens' in self.metadata['schema'] and \
           not isinstance(self.metadata['schema']['address_tokens'], dict):
            raise TypeError("%s 'schema.address_tokens' tag must be an object." % src_str)

        ###################
        # PATH ASSIGNMENT #
        ###################
        
        # set localfile, rawpath, dirtypath, and cleanpath values
        self.localfile = self.metadata['localfile']

        # by default, the OpenTabulate program defines the processing paths
        if self.default_paths:
            dirs = {
                'raw' : './data/raw',
                'dirty' : './data/dirty',
                'clean' : './data/clean',
                'pre' : './data/pre'
            }
            extensions = ('.csv', '.xml')
            basename = os.path.splitext(self.localfile)

            assert basename[1] in extensions, \
                "%s 'localfile' has an invalid file extension '%s'" % (src_str, basename[1])
            
            self.rawpath = os.path.join(dirs['raw'], self.localfile)
            self.dirtypath = os.path.join(dirs['dirty'], 'DIRTY-' + basename[0] + '.csv')
            self.dirtyerror = os.path.join(dirs['dirty'], 'ERR-DIRTY-' + basename[0] + '.csv')
            self.cleanpath = os.path.join(dirs['clean'], 'CLEAN-' + basename[0] + '.csv')
            self.cleanerror = os.path.join(dirs['clean'], 'ERR-CLEAN-' + basename[0] + '.csv')
            
            if 'pre' in self.metadata: # note: preprocessing script existence is checked before this step
                self.prepath = os.path.join(dirs['pre'], 'PRE-' + self.localfile)
                self.prepath_temp = os.path.join(dirs['pre'], 'PRE-TEMP' + self.localfile)

        # check entire source to make sure correct keys are being used
        for i in self.metadata:
            root_layer = ('localfile', 'localarchive', 'url', 'format', 'database_type',
                          'encoding', 'pre', 'post', 'header', 'schema', 'filter', 'provider')
            if i not in root_layer:
                raise ValueError("%s Invalid key in root_layer '%s' in source file" % (src_str, i))
            elif i == 'compression': # DEPRECATED - this should be removed later...
                raise ValueError("%s Version > 1.0.1 'compression' key removed")
            
        for i in self.metadata['format']:
            format_layer = ('type', 'header', 'quote', 'delimiter')
            if i not in format_layer:
                raise ValueError("%s Invalid key in format_layer '%s' in source file" % (src_str, i))

        for i in self.metadata['schema']:
            schema_layer = ('address_str_parse', 'address_str', 'address_tokens',
                            'phone', 'fax', 'email', 'website', 'tollfree',
                            'longitude', 'latitude')

            deprecated_schema_keys = ('comdist', 'region', 'hours', 'county')

            schema_layer = schema_layer + deprecated_schema_keys

            if self.metadata['database_type'] == 'business':
                bus_layer = ('legal_name', 'trade_name', 'business_type', 'business_no', 'bus_desc',
                             'licence_type', 'licence_no', 'start_date', 'closure_date', 'active',
                             'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3',
                             'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6',
                             'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2')

                deprecated_bus_keys = ('no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',
                                       'home_bus', 'munic_bus', 'nonres_bus', 'naics_desc',
                                       'facebook', 'twitter', 'linkedin', 'youtube', 'instagram')

                bus_layer = bus_layer + deprecated_bus_keys
                if not (i in schema_layer or i in bus_layer):
                    raise ValueError("%s Invalid key in bus_layer '%s' in source file" % (src_str, i))

            elif self.metadata['database_type'] == 'education':
                edu_layer = ('institution_name', 'institution_type', 'education_level', 'board_name',
                             'board_code', 'range', 'isced010', 'isced020', 'isced1',
                             'isced2', 'isced3', 'isced4+')

                deprecated_edu_keys = ('ins_code', 'school_yr')

                edu_layer = edu_layer + deprecated_edu_keys
                if not (i in schema_layer or i in edu_layer):
                    raise ValueError("%s Invalid key in edu_layer '%s' in source file" % (src_str, i))

            elif self.metadata['database_type'] == 'library':
                lib_layer = ('library_name','library_type','library_board')
                if not (i in schema_layer or i in lib_layer):
                    raise ValueError("%s Invalid key in lib_layer '%s' in source file" % (src_str, i))

            elif self.metadata['database_type'] == 'hospital':
                hosp_layer = ('hospital_name','hospital_type','health_authority')
                if not (i in schema_layer or i in hosp_layer):
                    raise ValueError("%s Invalid key in hosp_layer '%s' in source file" % (src_str, i))

            elif self.metadata['database_type'] == 'fire_station':
                fire_layer = ('fire_station_name')
                if not (i in schema_layer or i in fire_layer):
                    raise ValueError("%s Invalid key in fire_layer '%s' in source file" % (src_str, i))

        if 'address_tokens' in self.metadata['schema']:
            address_layer = ('street_no', 'street_name', 'unit', 'city', 'province', 'country', 'postal_code')
            for i in self.metadata['schema']['address_tokens']:
                if i not in address_layer:
                    raise ValueError("%s Invalid key in address_layer '%s' in source file" % (src_str, i))

        self.logger = logging.getLogger(self.localfile)
        

    def fetch_url(self):
        """
        Downloads a dataset by fetching its URL and writing to the raw directory 
        (currently './data/raw/').

        Returns:
            bool: True if download and writing succeeds, False otherwise.
        """
        if self.download_url == False:
            return False
        
        # use requests library if protocol is HTTP
        if self.metadata['url'][0:4] == "http":
            response = requests.get(self.metadata['url'])
            content = response.content
            # otherwise, use urllib to handle other protocols (e.g. FTP)
        else:
            response = req.urlopen(self.metadata['url'])
            content = response.read()

        '''
        # DEPRECATED #

        if 'compression' in self.metadata:
            if self.metadata['compression'] == "zip":
                with open('./data/raw/' + self.metadata['localarchive'], 'wb') as data:
                    data.write(content)
        else:
            with open('./data/raw/' + self.metadata['localfile'], 'wb') as data:
                data.write(content)
        '''
        
        return True

    '''
    # DEPRECATED #

    def archive_extraction(self):
        """
        Extracts data from an archive downloaded in the raw directory ('./data/raw'), 
        renaming the file if indicated by the source file.
        """
        if self.no_extract_flag == True:
            return False
        
        if self.metadata['compression'] == "zip":
            with ZipFile('./data/raw/' + self.metadata['localarchive'], 'r') as zip_file:
                archive_fname = self.metadata['localfile'].split(':')
                if len(archive_fname) == 1:
                    zip_file.extract(archive_fname[0], './data/raw/')
                else:
                    zip_file.extract(archive_fname[1], './data/raw/')
                    os.rename('./data/raw/' + archive_fname[1], './data/raw/' + self.localfile)

        return True
    '''

    def _convert_backward_compat_keys(self):
        """
        Legacy source key names are converted to the current version's standardized
        key names.
        """
        bcc_key_map = { "info" : "schema",
                        "full_addr" : "address_str_parse",
                        "address" : "address_tokens",
                        "bus_name" : "legal_name",
                        "lic_type" : "licence_type",
                        "lic_no" : "licence_no",
                        "bus_start_date": "start_date",
                        "bus_cease_date": "closure_date",
                        "ins_name": "institution_name",
                        "ins_type": "institution_type",
                        "edu_level": "education_level",
                        "fire_stn_name": "fire_station_name",
                        "prov/terr": "province",
                        "postcode": "postal_code"
        }

        def recursive_adjust(node):
            if not isinstance(node, dict):
                return
            else:
                mappable_keys = []
                # identify mappable keys
                for key in node:
                    recursive_adjust(node[key])
                    if key in bcc_key_map:
                        mappable_keys.append(key)
                # replace them accordingly
                for key in mappable_keys:
                    node[bcc_key_map[key]] = node.pop(key)
                return
            
        recursive_adjust(self.metadata)
