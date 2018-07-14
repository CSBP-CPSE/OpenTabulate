"""
A data processing tool for OpenBusinessRepository.

This module consists of tools to parse different file formats and convert 
them to CSVs based on the standards defined by the Data Exploration and 
Integration Lab at Statistics Canada (DEIL).

Written by Maksym Neyra-Nesterenko.
"""

from xml.etree import ElementTree
from os import remove as _rm
import csv
import copy


# -----------------
# --- VARIABLES ---
# -----------------

"""
Standardized fields:

[unused tags] street direction, street type, youtube, twitter, facebook, linkedin, instagram

[addresses] unit, house_number, road, city, prov, country, postcode, address !(address is a concatenation)
[contact] bus_name, trade_name, prim_phone, secn_phone, email, fax, website, toll_free
[location] latitude, longitude, comdist (community district/neighbourhood/..), ltln (latitude, longitude pair)
[info] bus_desc, active, no_employed,
[license] lic_status, lic_issued, lic_expd, lic_no !(lic_no depends on data set)

Synonyms: bus name, company name, operating name

"""

# The column names for the to-be-created CSV files
_FIELD_LABEL = ['bus_name', 'trade_name', 'bus_type', 'home_occup', 'bus_no', \
                'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active', \
                'full_addr', \
                'house_number', 'road', 'postcode', 'unit', 'city', 'prov', 'country', \
                'phone', 'fax', 'email', 'website', \
                'comdist', \
                'longitude', \
                'latitude', \
                'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', \
                'home_bus', \
                'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3', \
                'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6', \
                'naics_desc', \
                'facebook', 'twitter', 'linkedin', 'youtube', 'instagram']


# Address fields, boolean values required for parsers to handle duplicate entries correctly
ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'prov', 'country', 'postcode']

# Labels for the 'force' tag
FORCE_LABEL = ['city', 'region', 'country']

# Column order, keys expressed as libpostal parser labels
#lpsubf_order = {'house_number' : 0, 'road' : 1, 'unit' : 2, 'city' : 3, \
#                'region' : 4, 'country' : 5, 'postcode' : 6}


# ----------------------------------
# --- LABEL EXTRACTION FUNCTIONS ---
# ----------------------------------

def _xml_extract_labels(json_data):
    """
    Constructs a dictionary that stores only tags that were exclusively used in 
    a source file. This function is specific to the XML format since it returns 
    a header tag and uses XPath expressions.
                                                                                
    Note:
        This function is used by 'xml_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from a source file.

    Returns:
        The tag dictionary, header tag, and filename tag of the dataset to be parsed.
    """
    global ADDR_FIELD_LABEL
    global _FIELD_LABEL
    xml_fl = dict()                            # tag dictionary
    header_label = json_data['header']         # header tag
    filename = json_data['filename']           # filename tag
    
    # append existing data using XPath expressions (for parsing)
    for i in _FIELD_LABEL:
        if i in json_data['info'] and (not (i in ADDR_FIELD_LABEL)) and i != 'address':
            if isinstance(json_data['info'][i], list):
                xml_fl[i] = []
                for t in json_data['info'][i]:
                    xml_fl[i].append(".//" + t)
            else:
                xml_fl[i] = ".//" + json_data['info'][i]
        # short circuit evaluation
        elif ('address' in json_data['info']) and (i in json_data['info']['address']):
            XPathString = ".//" + json_data['info']['address'][i]
            xml_fl[i] = XPathString
        elif ('force' in json_data) and (i in json_data['force']):
            xml_fl[i] = 'DPIFORCE'
    return xml_fl, header_label, filename


def _csv_extract_labels(json_data):
    """
    Constructs a dictionary that stores only tags that were exclusively used in 
    a source file. In contrast to 'xml_extract_labels', a header is not required 
    in the source file.
                                                                                
    Note:
        This function is used by 'csv_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from a source file.

    Returns:
        The tag dictionary and filename tag of the dataset to be parsed.
    """
    global _FIELD_LABEL
    global ADDR_FIELD_LABEL
    fd = dict()                      # tag dictionary
    filename = json_data['filename'] # filename tag

    for i in _FIELD_LABEL:
        if i in json_data['info'] and (not (i in ADDR_FIELD_LABEL)):
            fd[i] = json_data['info'][i]
        elif ('address' in json_data['info']) and (i in json_data['info']['address']):
            AddressVarField = json_data['info']['address'][i]
            fd[i] = AddressVarField
        elif ('force' in json_data) and (i in json_data['force']):
            fd[i] = 'DPIFORCE'
    return fd, filename



# --------------------------------
# --- PARSING HELPER FUNCTIONS ---
# --------------------------------

def _xml_empty_element_handler(element):
    """
    The 'xml.etree' module returns 'None' for text of empty-element tags. Moreover, 
    if the element cannot be found, the element is 'None'. This function is defined 
    to handle these cases.

    Note:
        This function is used by 'xml_parse'.

    Args:
        element: A node in the XML tree.

    Returns:
        'True' is returned if element's tag is missing from the header. From here,
        'xml_parse' returns a detailed error message of the missing tag and 
        terminates the data processing.

        Otherwise, return the appropriate field contents.
    """
    if element is None: # if the element is missing, return error
        return True
    if not (element.text is None):
        return element.text
    else:
        return ''


# -------------------------
# --- PARSING FUNCTIONS ---
# -------------------------

def xml_parse(json_data):
    """
    Parses a dataset in XML format using the xml.etree.ElementTree module and 
    extracts the necessary information to rewrite the data set into CSV format, 
    as specified by a source file.

    Args:
        json_data: dictionary obtained by json.load when read from a source file

    Raises:
        ElementTree.ParseError: Incorrect XML format of the specified dataset.
        
    Returns:
        Return values are interpreted by 'process.py' as follows:
        '0' : Successful reformatting.
        '1' : Incorrect formatting of XML dataset.
        '2' : Missing element tag within a header tag.
    """
    global FORCE_LABEL
    
    tags, header, filename = _xml_extract_labels(json_data)

    try:
        tree = ElementTree.parse('./raw/' + filename)
    except ElementTree.ParseError:
        return 1
    
    root = tree.getroot()

    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"

    csvfile = open('./dirty/' + dirty_file, 'w')
    cprint = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    first_row = [f for f in tags]
    cprint.writerow(first_row)
    
    for element in root.findall(header):
        row = []
        for key in tags:
            if isinstance(tags[key], list) and key not in FORCE_LABEL:
                count = 0
                for i in tags[key]:
                    entry = ''
                    count += 1
                    subelement = element.find(i)
                    subel_content = _xml_empty_element_handler(subelement)
                    if subel_content == True:
                        print("[E] Header '", element.tag, ' ', element.attrib, "' is missing '", tags[key], "'.", sep='')
                        csvfile.close()
                        _rm('./dirty/' + dirty_file)
                        return 2
                    else:
                        if count == len(tags[key]):
                            entry += subel_content
                        else:
                            entry += subel_content + ' '
                row.append(entry)
                continue

            if tags[key] != 'DPIFORCE':
                subelement = element.find(tags[key])
                subel_content = _xml_empty_element_handler(subelement)
                if subel_content == True:
                    print("[E] Header '", element.tag, ' ', element.attrib, "' is missing '", tags[key], "'.", sep='')
                    csvfile.close()
                    _rm('./dirty/' + dirty_file)
                    return 2
                else:
                    row.append(subel_content)
            else:
                row.append(json_data['force'][key])
        cprint.writerow(row)
    csvfile.close()
    return 0


def csv_parse(json_data):
    """
    Parses a dataset in CSV format using the csv module and extracts the necessary 
    information to rewrite the data set into CSV format, as specified by a source file.
                                                                                
    Args:
        json_data: dictionary obtained by json.load when read from a source file

    Returns:
        Return values are interpreted by 'process.py' as follows:
        '0' : Successful reformatting.
        '1' : A tag value defined from a source file does not match the dataset's metadata.
    """

    global FORCE_LABEL

    tags, filename = _csv_extract_labels(json_data)
    
    # construct csv parser
    csv_file_read = open('./pp/' + filename, 'r', encoding='utf-8', errors='ignore', newline='') 
    cparse = csv.DictReader(csv_file_read)

    # construct csv writer to dirty
    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"
    
    csv_file_write = open('./dirty/' + dirty_file, 'w')
    cprint = csv.writer(csv_file_write, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    first_row = [f for f in tags]
    cprint.writerow(first_row)

    try:
        for entity in cparse:
            row = []
            for key in tags:
                if isinstance(tags[key], list) and key not in FORCE_LABEL:
                    count = 0
                    entry = ''
                    for i in tags[key]:
                        count += 1
                        if count == len(tags[key]):
                            entry += entity[i]
                        else:
                            entry += entity[i] + ' '
                    row.append(entry)
                    continue

                if tags[key] != 'DPIFORCE':
                    entry = entity[tags[key]]
                else:
                    entry = json_data['force'][key]
                row.append(entry)
            cprint.writerow(row)
    except KeyError:
        print("[E] '", tags[key], "' is not a field name in the CSV file.", sep='')
        # close reader / writer and delete the partially written data file
        csv_file_read.close()
        csv_file_write.close()
        _rm('./dirty/' + dirty_file)
        return 1
    
    # success
    csv_file_read.close()
    csv_file_write.close()
    return 0



    
"""
def CA_Address_Split(line, flist):
    tokens = parse_address(line, flist)
    
    # add 'empty' tokens that were not added by parse_address
    for i in flist:
        if not (i in [t[1] for t in tokens]):
            tokens.append(('',i))
            
    # keep address tokens
    tokens = [t for t in tokens if t[1] in flist]

    # split house numbers separated by hyphen
    TEMP = ([t for t in tokens if t[1] == 'house_number'][0])[0]
    if '-' in TEMP:
        sp = TEMP.split('-')
        UNIT = sp[0]
        STREET_NO = sp[1]

        for i in tokens:
            if i[1] == 'house_number':
                tokens.remove(i)
                tokens.append((STREET_NO,'house_number'))
            elif i[1] == 'unit':
                tokens.remove(i)
                tokens.append((UNIT,'unit'))

    # sort tokens
    tokens = sorted(tokens, key=lambda x: lpsubf_order[x[1]])

    return tokens
"""
