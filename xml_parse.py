"""
* Statistics Canada - Center for Special Business Projects - DEIL *

~ Maksym Neyra-Nesterenko

This script serves as a .xml file parser

CURRENT ISSUES:
- How do we associate child entries (e.g. leaves) to parent entries in .xml parsing?
  Some parent nodes may have missing data entries, so to correctly parse, each row in
  the processed .csv file must correspond to <estab> in uslist2018-05-24-18-25.xml
- Missing fields from format.json must be handled correctly
  * Data entries must be stored in a dictionary
  * If the entry is not there, return None
- Utilizing 'type' and 'filename/path' [for a more general script which calls modules]

"""

from xml.etree import ElementTree
import json
import csv

# load .json format file
with open('format.json') as f:
    data = json.load(f)

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
tree = ElementTree.parse(filename)
root = tree.getroot()

new_file = filename.partition(".")[0] + ".csv"

with open(new_file, 'w') as csvfile:
    dp = csv.writer(csvfile, delimiter=' ', quotechar='"', quoting=csv.QUOTE_ALL)
    for element in root.findall(header):
        row = []
        for key in data_field:
            subelement = element.find(data_field[key])
            if not subelement is None:
                row.append(subelement.text)
            else:
                row.append(" ")
        dp.writerow(row)
