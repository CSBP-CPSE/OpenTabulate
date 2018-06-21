"""
A data processing tool for OpenBusinessRepository.

This module consists of tools to parse different file formats and convert them to CSVs based on 
the standards defined by the Data Exploration and Integration Lab at Statistics Canada (DEIL).

Written by Maksym Neyra-Nesterenko.
"""

from xml.etree import ElementTree
from postal.parser import parse_address
from os import remove
import csv
import copy

field = ['name', 'bus_type', 'address', 'st_number', 'st_name', 'postcode', 'unit', \
         'city', 'region', 'country', 'phone', 'email', 'website', \
         'longitude', 'latitude', 'reg_date', 'exp_date', 'status', 'specid']

lpsubf_order = {'house_number' : 0, 'road' : 1, 'unit' : 2}

def xml_hash_table_gen(json_data):
    """
    Constructs a filtered dictionary to be used by the XML parser.

    Note:
        This function is used by 'xml_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from DPI.

    Returns:
        The filtered dictionary, header entry, and filename of the dataset to be parsed.
    """
    global field
    field_dict = dict()
    header_entry = json_data['info']['header']
    filename = json_data['filename']

    # append existing data using XPath expressions (for parsing)
    for i in field:
        if i in json_data['info'] and i != 'address':
            field_dict[i] = ".//" + json_data['info'][i]
        elif i == 'address' and isinstance(json_data['info'][i], str):
            field_dict[i] = ".//" + json_data['info'][i]
        elif (i == 'st_number' or i == 'st_name' or i == 'unit') and isinstance(json_data['info']['address'], dict):
            field_dict[i] = ".//" + json_data['info']['address'][i]
    return field_dict, header_entry, filename

# -- IN DEVELOPMENT --
def csv_hash_table_gen(json_data):
    """
    Constructs a filtered dictionary to be used by the CSV parser.

    Note:
        This function is used by 'csv_parse'.

    Args:
        json_data: dictionary obtained by json.load when read from DPI.

    Returns:
        The filtered dictionary, header entry, and filename of the dataset to be parsed.
    """
    global field
    field_dict = dict()
    # HEADER ENTRY NOT NEEDED FOR CSV !!!
    header_entry = json_data['info']['header']
    filename = json_data['filename']

    for i in field:
        if i in json_data['info'] and i != 'address':
            field_dict[i] = json_data['info'][i]
        elif i == 'address' and isinstance(json_data['info'][i], str):
            field_dict[i] = json_data['info'][i]
        elif (i == 'st_number' or i == 'st_name' or i == 'unit') and isinstance(json_data['info']['address'], dict):
            field_dict[i] = json_data['info']['address'][i]
    return field_dict, header_entry, filename
    

def canadian_Address_Parse(line):
    tokens = parse_address(line)
    
    # add 'empty' tokens that were not added by parse_address
    for i in lpsubf_order:
        if not (i in [t[1] for t in tokens]):
            tokens.append(('',i))
            
    # keep address tokens
    tokens = [t for t in tokens if t[1] == 'unit' or \
              t[1] == 'house_number' or t[1] == 'road']

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
    if (not element is None) and (not element.text is None):
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
    data_field, header, filename = xml_hash_table_gen(json_data)
    # -- REDEFINE ORDER OF KEYS OF 'data_field' HERE --
    # CURRENTLY STUBBED
    #data_field = order_hash_keys(data_field)
    
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
    if 'address' in data_field:
        temp_var = [f for f in data_field].index('address')
        temp_list = [f for f in data_field if f != 'address']
        for i in lpsubf_order:
            temp_list.insert(temp_var, i)
            temp_var += 1
        dp.writerow(temp_list)
    else:
        dp.writerow([f for f in data_field])

    for element in root.findall(header):
        row = []
        for key in data_field:
            if key == 'address':
                subelement = element.find(data_field[key])
                if (subelement is None) or (subelement.text is None):
                    row.append('')
                    row.append('')
                    row.append('')
                    continue
                # parse address
                tokens = canadian_Address_Parse(subelement.text)
                
                # add data to csv
                for t in tokens:
                    if t[0] != '':
                        row.append(t[0].upper())
                    else:
                        row.append('')
            else: # non-address keys
                subelement = element.find(data_field[key])
                row = xml_NoneType_handler(row, subelement)
        dp.writerow(row)
    csvfile.close()
    return 0


def csv_parse(data):
    data_field, header, filename = csv_hash_table_gen(data)
    
    # -- REDEFINE ORDER OF KEYS OF 'data_field' HERE --
    # CURRENTLY STUBBED
    #data_field = order_hash_keys(data_field)

    # construct csv parser
    csv_file_read = open('./pp/' + filename, 'r', encoding='utf-8', newline='') # errors='ignore'
    cparse = csv.DictReader(csv_file_read)

    # construct csv writer to dirty
    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"
    
    csv_file_write = open('./dirty/' + dirty_file, 'w')
    cprint = csv.writer(csv_file_write, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    if 'address' in data_field:
        temp_var = [f for f in data_field].index('address')
        temp_list = [f for f in data_field if f != 'address']
        for i in lpsubf_order:
            temp_list.insert(temp_var, i)
            temp_var += 1
        cprint.writerow(temp_list)
    else:
        cprint.writerow([f for f in data_field])
    try:
        for entity in cparse:
            row = []
            for key in data_field:
                if key == 'address':
                    entry = entity[data_field[key]]
                    tokens = canadian_Address_Parse(entry)
                    # add data to csv
                    for t in tokens:
                        if t[0] != '':
                            row.append(t[0].upper())
                        else:
                            row.append('')
                else: # non-address keys
                    entry = entity[data_field[key]]
                    row.append(entry)
            cprint.writerow(row)
    except KeyError:
        # close reader / writer and delete the partially written data file
        csv_file_read.close()
        csv_file_write.close()
        remove('./dirty/' + dirty_file)
        return 2
    
    # success
    csv_file_read.close()
    csv_file_write.close()
    return 0
