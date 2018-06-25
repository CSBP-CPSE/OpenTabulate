"""
A data processing tool for OpenBusinessRepository.

This module consists of tools to parse different file formats and convert them to CSVs based on 
the standards defined by the Data Exploration and Integration Lab at Statistics Canada (DEIL).

Written by Maksym Neyra-Nesterenko.
"""

from xml.etree import ElementTree
from os import remove
import csv
# from postal.parser import parse_address
import copy

# The column names for the to-be-created CSV files
FIELD_LABEL = ['name', 'bus_type', 'address', 'house_number', 'road', 'postcode', 'unit', \
         'city', 'region', 'country', 'phone', 'email', 'website', 'longitude', \
         'latitude', 'reg_date', 'exp_date', 'status', 'specid']

# Address fields, boolean values required for parsers to handle duplicate entries correctly
ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'region', 'country', 'postcode']

# Column order, keys expressed as libpostal parser labels
#lpsubf_order = {'house_number' : 0, 'road' : 1, 'unit' : 2, 'city' : 3, \
#                'region' : 4, 'country' : 5, 'postcode' : 6}

def xml_extract_labels(json_data):
    """
    Constructs a filtered dictionary to be used by the XML parser.

    Note:
        This function is used by 'xml_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from DPI.

    Returns:
        The filtered dictionary, header entry, and filename of the dataset to be parsed.
    """
    global ADDR_FIELD_LABEL
    global FIELD_LABEL
    xml_fl = dict()
    header_label = json_data['info']['header']
    filename = json_data['filename']

    # append existing data using XPath expressions (for parsing)
    for i in FIELD_LABEL:
        if i in json_data['info'] and (not (i in ADDR_FIELD_LABEL)) and i != 'address':
            xml_fl[i] = ".//" + json_data['info'][i]
        elif i in json_data['info']['address']:
            XPathString = ".//" + json_data['info']['address'][i]
            xml_fl[i] = XPathString
    return xml_fl, header_label, filename


def csv_hash_table_gen(json_data):
    """
    Constructs a filtered dictionary to be used by the CSV parser.

    Note:
        This function is used by 'csv_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from DPI.

    Returns:
        The filtered dictionary and filename of the dataset to be parsed.
    """
    global FIELD_LABEL
    global ADDR_FIELD_LABEL
    fd = dict()
    filename = json_data['filename']

    for i in FIELD_LABEL:
        if i in json_data['info'] and (not (i in ADDR_FIELD_LABEL)):
            fd[i] = json_data['info'][i]
        elif i in json_data['info']['address']:
            AddressVarField = json_data['info']['address'][i]
            fd[i] = AddressVarField
    return fd, filename
    
# -- IN DEVELOPMENT --
#def order_hash_keys(dictionary):
#    # To do for later
#    print("STUB")
#    return dictionary


# handle elements of type 'None' in XML tree
def xml_NoneType_handler(row_list, element):
    """
    Handles XML data that has missing or empty elements. Such elements have an empty string
    appended to the CSV file to avoid error calls. Otherwise, valid elements are appended
    without concern.

    Note:
        This function is used by 'xml_parse'.

    Args:
        row_list: A list of fields that will appended to the CSV file as a row.
        element: A node in the XML tree.

    Returns:
        The list to be appended as a row in the resulting CSV file.
    """
    if element is None: # if the element is missing, return error
        return True
    if not (element.text is None):
        row_list.append(element.text.upper())
    else:
        row_list.append('')
    return row_list


def xml_parse(json_data):
    """
    Parses an XML file using the xml.etree.ElementTree module and extracts the necessary 
    information to rewrite the data set into a CSV file.

    Args:
        json_data: dictionary obtained by json.load when read from DPI.

    Raises:
        ...
    """
    global ADDR_FIELD_LABEL
    data_field, header, filename = xml_extract_labels(json_data)

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
    dp = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    first_row = [f for f in data_field]
    dp.writerow(first_row)
        
    for element in root.findall(header):
        row = []
        for key in data_field:
            subelement = element.find(data_field[key])
            XML_VALID_ENTRY = xml_NoneType_handler(row, subelement)
            if XML_VALID_ENTRY == True:
                print("[E] Header '", element.tag, ' ', element.attrib, "' is missing '", data_field[key], "'.", sep='')
                csvfile.close()
                remove('./dirty/' + dirty_file)
                return 2
            else:
                row = XML_VALID_ENTRY
        dp.writerow(row)
    csvfile.close()
    return 0


def csv_parse(data):
    global ADDR_FIELD_LABEL
    data_field, filename = csv_hash_table_gen(data)
    
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
    first_row = [f for f in data_field]
    cprint.writerow(first_row)

    try:
        for entity in cparse:
            row = []
            for key in data_field:
                entry = entity[data_field[key]]
                row.append(entry)
            cprint.writerow(row)
    except KeyError:
        print("[E] '", data_field[key], "' is not a field name in the CSV file.", sep='')
        # close reader / writer and delete the partially written data file
        csv_file_read.close()
        csv_file_write.close()
        remove('./dirty/' + dirty_file)
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
