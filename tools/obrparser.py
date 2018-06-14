"""
Statistics Canada - Center for Special Business Projects - DEIL

Maksym Neyra-Nesterenko

A collection of parsing functions for different file formats.
"""

from xml.etree import ElementTree
from postal.parser import parse_address
import csv
import copy

# Global variables
field = ['name', 'address', 'st_number', 'st_name', 'unit', \
         'city', 'region', 'phone', 'postcode']

# Address parse ordering
lpsubf_order = {'house_number' : 0, 'road' : 1, 'unit' : 2}

# Hash table generation
def xml_hash_table_gen(json_data):
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
    return kfield_dict, header_entry, filename
    

# -- IN DEVELOPMENT -- 
def addr_parse():
    # To do for later
    print("STUB")

# -- IN DEVELOPMENT --
#def order_hash_keys(dictionary):
#    # To do for later
#    print("STUB")
#    return dictionary


# handle elements of type 'None' in XML tree
def xml_NoneType_handler(row_list, element):
    # append data to csv and handle missing subelements
    if (not element is None) and (not element.text is None):
        row_list.append(element.text.upper())
    else:
        row_list.append('')
    return row_list


# XML data processing
def xml_parse(json_data, obr_p_path):
    # build hash table
    data_field, header, filename = xml_hash_table_gen(json_data)

    # -- REDEFINE ORDER OF KEYS OF 'data_field' HERE --
    # CURRENTLY STUBBED
    #data_field = order_hash_keys(data_field)
    
    # parse xml and write to csv

    # -- HANDLE PARSING FAILURE HERE --
    # -- ADDITIONALLY, HANDLE NON-EXISTENT FILE/PATH HERE OR IN PROCESS.PY AT %%% alert %%% --
    tree = ElementTree.parse(obr_p_path + '/preprocessed/' + filename)
    root = tree.getroot()

    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + ".csv"

    csvfile = open(obr_p_path + '/dirty/' + dirty_file, 'w')
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
                # ---- --
                # -- ~ handle countries properly - see pypostal doc --
                # ---- --
                tokens = parse_address(subelement.text)

                # add 'empty' tokens that were not added by parse_address
                for i in lpsubf_order:
                    if not (i in [t[1] for t in tokens]):
                        tokens.append(('',i))

                # keep address tokens
                tokens = [t for t in tokens if t[1] == 'unit' or \
                          t[1] == 'house_number' or t[1] == 'road']

                # sort tokens
                tokens = sorted(tokens, key=lambda x: lpsubf_order[x[1]])

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

# -- IN DEVELOPMENT --
def csv_parse(data,obr_p_path):
    data_field, header, filename = csv_hash_table_gen(data)
    
    # -- REDEFINE ORDER OF KEYS OF 'data_field' HERE --
    # CURRENTLY STUBBED
    #data_field = order_hash_keys(data_field)
    
    # construct csv parser
    csv_file_read = open(obr_p_path + '/preprocessed/' + filename, 'r', encoding='latin-1', newline='')
    cparse = csv.DictReader(csv_file_read)

    # construct csv writer to dirty
    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + ".csv"
    
    csv_file_write = open(obr_p_path + '/dirty/' + dirty_file, 'w')
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

    for entity in cparse:
        row = []
        for key in data_field:
            if key == 'address':
                entry = entity[data_field[key]]
                # ---- --
                # -- ~ handle countries properly - see pypostal doc --
                # ---- --
                tokens = parse_address(entry)

                # add 'empty' tokens that were not added by parse_address
                for i in lpsubf_order:
                    if not (i in [t[1] for t in tokens]):
                        tokens.append(('',i))

                # keep address tokens
                tokens = [t for t in tokens if t[1] == 'unit' or \
                          t[1] == 'house_number' or t[1] == 'road']

                # sort tokens
                tokens = sorted(tokens, key=lambda x: lpsubf_order[x[1]])

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
        
    csv_file_read.close()
    csv_file_write.close()
