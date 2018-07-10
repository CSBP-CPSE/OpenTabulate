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
import json
import copy


# -----------------
# --- VARIABLES ---
# -----------------

# The column names for the to-be-created CSV files
_FIELD_LABEL = ['name', 'industry', 'address', 'house_number', 'road', 'postcode', 'unit', \
         'city', 'region', 'country', 'phone', 'email', 'website', 'longitude', \
         'latitude', 'reg_date', 'exp_date', 'status', 'specid']

# Address fields, boolean values required for parsers to handle duplicate entries correctly
ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'region', 'country', 'postcode']

# Labels for the 'default' tag
DEFAULT_LABEL = ['city', 'region', 'country']

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
            xml_fl[i] = ".//" + json_data['info'][i]
        # short circuit evaluation
        elif ('address' in json_data['info']) and (i in json_data['info']['address']):
            XPathString = ".//" + json_data['info']['address'][i]
            xml_fl[i] = XPathString
        elif ('default' in json_data) and (i in json_data['default']):
            xml_fl[i] = 'DPIDEFAULT'
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
        elif ('default' in json_data) and (i in json_data['default']):
            fd[i] = 'DPIDEFAULT'
    return fd, filename


def _json_extract_labels(json_data):
    """
    Constructs a dictionary that stores only tags that were exclusively used in 
    a source file. This function is specific to the JSON format and requires a 
    header tag.
                                                                                
    Note:
        This function is used by 'json_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from a source file.

    Returns:
        The tag dictionary, header tag, and filename tag of the dataset to be parsed.
    """
    global ADDR_FIELD_LABEL
    global _FIELD_LABEL
    json_fl = dict()                           # tag dictionary
    header_label = json_data['header']         # header tag
    filename = json_data['filename']           # filename tag
    
    # append existing data using XPath expressions (for parsing)
    for i in _FIELD_LABEL:
        if i in json_data['info'] and (not (i in ADDR_FIELD_LABEL)) and i != 'address':
            json_fl[i] =  json_data['info'][i]
        # short circuit evaluation
        elif ('address' in json_data['info']) and (i in json_data['info']['address']):
            AddressFieldVar = json_data['info']['address'][i]
            json_fl[i] = AddressFieldVar
        elif ('default' in json_data) and (i in json_data['default']):
            json_fl[i] = 'DPIDEFAULT'
    return json_fl, header_label, filename


# --------------------------------
# --- PARSING HELPER FUNCTIONS ---
# --------------------------------

def _xml_empty_element_handler(row, element):
    """
    The 'xml.etree' module returns 'None' for text of empty-element tags. Moreover, 
    if the element cannot be found, the element is 'None'. This function is defined 
    to handle these cases.

    Note:
        This function is used by 'xml_parse'.

    Args:
        row: A list of fields that will appended to the resulting CSV file as a row.
        element: A node in the XML tree.

    Returns:
        'True' is returned if element's tag is missing from the header. From here,
        'xml_parse' returns a detailed error message of the missing tag and 
        terminates the data processing.

        Otherwise, return the updated row to 'xml_parse'.
    """
    if element is None: # if the element is missing, return error
        return True
    if not (element.text is None):
        row.append(element.text)
    else:
        row.append('')
    return row


def _json_tree_search(root, key):
    for child_key in root:
        if child_key == key:
            return root[child_key]
        # --- DEBUG: warning, list may be a tuple ---
        if not (isinstance(root[child_key], dict) or isinstance(root[child_key], list)): 
            # child is a leaf
            return None, False
        else:
            # child is an internal node
            node = _json_tree_search(root[child_key], key)
            if node == None:
                # this node does not contain what we are looking for
                pass
            else:
                return node

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
            if tags[key] != 'DPIDEFAULT':
                subelement = element.find(tags[key])
                errhandle = _xml_empty_element_handler(row, subelement)
                if errhandle == True:
                    print("[E] Header '", element.tag, ' ', element.attrib, "' is missing '", tags[key], "'.", sep='')
                    csvfile.close()
                    _rm('./dirty/' + dirty_file)
                    return 2
                else:
                    row = errhandle
            else:
                row.append(json_data['default'][key])
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
                if tags[key] != 'DPIDEFAULT':
                    entry = entity[tags[key]]
                else:
                    entry = json_data['default'][key]
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


def json_parse(json_data):
    """
    --- docstring to be added ---
    """
    tags, header, filename = _json_extract_labels(json_data)

    jf = open('./raw/' + filename, 'r')
    jsondata = json.load(jf)
    
    jf.close()


    
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
