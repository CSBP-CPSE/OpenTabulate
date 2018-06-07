"""
* Statistics Canada - Center for Special Business Projects - DEIL *

~ Maksym Neyra-Nesterenko

A collection of parsing functions for different file formats.

ISSUES:
- How do we associate child entries (e.g. leaves) to parent entries in .xml parsing?
  Some parent nodes may have missing data entries, so to correctly parse, each row in
  the processed .csv file must correspond to <estab> in uslist2018-05-24-18-25.xml
"""

from xml.etree import ElementTree
import csv

def xml_parse(data,obr_p_path):
    # construct hash table for field names
    field_names = ['name', 'address', 'city', 'region', 'postcode', 'phone']
    data_field = dict()

    header = data['info']['header']
    filename = data['filename']

    for i in field_names:
        try:
            data_field[i] = ".//" + data['info'][i]
        except KeyError: # if a key is missing, ignore
            continue

    # parse DATA.xml file and write output to DATA.csv
    tree = ElementTree.parse(obr_p_path + '/ppdata/' + filename)
    root = tree.getroot()

    new_file = filename.partition(".")[0] + ".csv"

    with open(obr_p_path + '/dirty/' + new_file, 'w') as csvfile:
        dp = csv.writer(csvfile, delimiter=',', quotechar='\'', quoting=csv.QUOTE_ALL)
        for element in root.findall(header):
            row = []
            for key in data_field:
                subelement = element.find(data_field[key])
                if not subelement is None:
                    row.append(subelement.text)
                else:
                    row.append(" ")
            dp.writerow(row)
    csvfile.close()
