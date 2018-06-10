"""
Statistics Canada - Center for Special Business Projects - DEIL

Maksym Neyra-Nesterenko

A collection of parsing functions for different file formats.
"""

from xml.etree import ElementTree
from postal.parser import parse_address
import csv

# Global variables
field = ['name', 'address', 'st_number', 'st_name', 'unit', \
         'city', 'region', 'phone', 'postcode']

lpsubf_order = {'house_number' : 0, 'road' : 1, 'unit' : 2}

def xml_hash_table_gen(json_data):
    global field
    field_dict = dict()
    header_entry = json_data['info']['header']
    filename = json_data['filename']

    for i in field:
        try:
            if i == 'st_number' or i == 'st_name' or i == 'unit':
                field_dict[i] = ".//" + json_data['info']['address'][i]
            else:
                field_dict[i] = ".//" + json_data['info'][i]
        except KeyError: # if a key is missing, ignore
            continue
        except TypeError: # if 'address' is a list, ignore
            continue
    # -- DEBUG -> print(field_dict, header_entry, filename)
    return field_dict, header_entry, filename


def addr_parse():
    # To do for later
    print("STUB")

    
def xml_NoneType_handler(row_list, element):
    # -- TESTING --
    # append data to .csv / handle missing subelement
    if (not element is None) and (not element.text is None):
        row_list.append(element.text.upper())
    else:
        row_list.append(" ")
    return row_list

    
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
                # -- TESTING --
                if key == 'address':
                    subelement = element.find(data_field[key])
                    if subelement is None:
                        row.append(" ")
                        row.append(" ")
                        row.append(" ")
                        continue
                    # -- TESTING ~ handle counries properly --
                    tokens = parse_address(subelement.text + " , Canada")
                    # add 'empty' tokens that were not added by parse_address
                    for i in lpsubf_order:
                        try:
                            [t[1] for t in tokens].index(i)
                        except ValueError:
                            tokens.append(('',i))
                    # keep address tokens
                    tokens = [t for t in tokens if t[1] == 'unit' or \
                              t[1] == 'house_number' or t[1] == 'road']
                    # sort tokens
                    tokens = sorted(tokens, key=lambda x: lpsubf_order[x[1]])
                    for t in tokens:
                        if t[0] != '':
                            row.append(t[0].upper())
                        else:
                            row.append(" ")
                    continue
                else:
                    subelement = element.find(data_field[key])
                    row = xml_NoneType_handler(row, subelement)
            dp.writerow(row)
    csvfile.close()


def csv_parse(data,obr_p_path):
    data_field, header, filename = xml_hash_table_gen(json_data)
