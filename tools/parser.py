"""
Statistics Canada - Center for Special Business Projects - DEIL

Maksym Neyra-Nesterenko

A collection of parsing functions for different file formats.
"""

from xml.etree import ElementTree
#from postal.parser import parse_address
import csv

# Global variables
field = ['name', 'unit', 'st_number', 'st_name', 'address', 'city', 'region', 'postcode', 'phone']


def xml_hash_table_gen(json_data):
    global field
    field_dict = dict()
    header_entry = json_data['info']['header']
    filename = json_data['filename']
    
    for i in field:
        try:
            field_dict[i] = ".//" + json_data['info'][i]
        except KeyError: # if a key is missing, ignore
            continue
    return field_dict, header_entry, filename


def addr_parse():
    # To do for later
    print("STUB")


def xml_parse(json_data, obr_p_path):
    # build hash table
    data_field, header, filename = xml_hash_table_gen(json_data)

    # parse xml and write to csv
    tree = ElementTree.parse(obr_p_path + '/preprocessed/' + filename)
    root = tree.getroot()

    dirty_file = filename.partition(".")[0] + ".csv"

    with open(obr_p_path + '/dirty/' + dirty_file, 'w') as csvfile:
        dp = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for element in root.findall(header):
            row = []
            for key in data_field:
                if (key == 'address') and isinstance(data_field[key], dict):
                    # do a subelement search for street name, number, and unit number
                    # inside this if statement
                    print("STUB")
                elif (key == 'address') and isinstance(data_field[key], str):
                    # parse the address and then append street name, number, etc.
                    # CURRENTLY A STUB, SOON TO CHANGE
                    #tokens = parse_address(data_field[key])
                    # SEARCH 'tokens' TO APPEND APPROPRIATE ITEMS
                    subelement = element.find(data_field[key])
                    if not subelement is None:
                        row.append(subelement.text)
                    else:
                        row.append(" ")
                else:
                    subelement = element.find(data_field[key])
                    # handles missing data fields
                    if not subelement is None:
                        row.append(subelement.text)
                    else:
                        row.append(" ")
            dp.writerow(row)
    csvfile.close()


def csv_parse(data,obr_p_path):
    data_field, header, filename = xml_hash_table_gen(json_data)
