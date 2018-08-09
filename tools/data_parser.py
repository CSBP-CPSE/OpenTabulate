"""
A data processing tool for OpenBusinessRepository.

This module consists of tools to parse different file formats and convert 
them to CSVs based on the standards defined by the Data Exploration and 
Integration Lab at Statistics Canada (DEIL).

Written by Maksym Neyra-Nesterenko.
"""

from xml.etree import ElementTree
#from postal.parser import parse_address
import csv
import copy
import operator
import re

# -----------------
# --- VARIABLES ---
# -----------------

# Standardized column names for source files - for usage and
# documentation, see 'docs/CONTRIB.md' in the repository
_FIELD_LABEL = ['bus_name', 'trade_name', 'bus_type', 'bus_no', 'bus_desc', \
                'lic_type', 'lic_no', 'bus_start_date', 'bus_cease_date', 'active', \
                'full_addr', \
                'house_number', 'road', 'postcode', 'unit', 'city', 'prov', 'country', \
                'phone', 'fax', 'email', 'website', 'tollfree',\
                'comdist', 'region', \
                'longitude', \
                'latitude', \
                'no_employed', 'no_seasonal_emp', 'no_full_emp', 'no_part_emp', 'emp_range',\
                'home_bus', 'munic_bus', 'nonres_bus', \
                'exports', 'exp_cn_1', 'exp_cn_2', 'exp_cn_3', \
                'naics_2', 'naics_3', 'naics_4', 'naics_5', 'naics_6', \
                'naics_desc', \
                'qc_cae_1', 'qc_cae_desc_1', 'qc_cae_2', 'qc_cae_desc_2', \
                'facebook', 'twitter', 'linkedin', 'youtube', 'instagram']


# Address fields
ADDR_FIELD_LABEL = ['unit', 'house_number', 'road', 'city', 'prov', 'country', 'postcode']

# Labels for the 'force' tag
FORCE_LABEL = ['city', 'prov', 'country']

# Column order, keys expressed as libpostal parser labels
ADDR_LABEL_TO_POSTAL = {'house_number' : 'house_number', \
                        'road' : 'road', \
                        'unit' : 'unit', \
                        'city' : 'city', \
                        'prov' : 'state', \
                        'country' : 'country', \
                        'postcode' : 'postcode' }


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
    filename = json_data['file']               # filename tag
    
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
    filename = json_data['file']     # filename tag

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
        return ''
    if not (element.text is None):
        return element.text
    else:
        return ''


# -------------------------
# --- PARSING FUNCTIONS ---
# -------------------------

def xml_parse(json_data, enc, address_parser):
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
    """
    global FORCE_LABEL
    global ADDR_FIELD_LABEL
    global ADDR_LABEL_TO_POSTAL
    
    tags, header, filename = _xml_extract_labels(json_data)

    try:
        xmlp = ElementTree.XMLParser(encoding=enc)
        tree = ElementTree.parse('./pddir/raw/' + filename, parser=xmlp)
    except ElementTree.ParseError:
        return 1, ''
    
    root = tree.getroot()

    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"

    csvfile = open('./pddir/dirty/' + dirty_file, 'w')
    cprint = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    first_row = [f for f in tags]
    if "full_addr" in first_row:
        ind = first_row.index("full_addr")
        first_row.pop(ind)
        for af in reversed(ADDR_FIELD_LABEL):
            first_row.insert(ind, af)
    cprint.writerow(first_row)

    for element in root.iter(header):
        row = []
        for key in tags:
            if isinstance(tags[key], list) and key not in FORCE_LABEL:
                count = 0
                entry = ''
                for i in tags[key]:
                    count += 1
                    subelement = element.find(i)
                    subel_content = _xml_empty_element_handler(subelement)
                    if count == len(tags[key]):
                        entry += subel_content
                    else:
                        entry += subel_content + ' '
                entry = _quick_scrub(entry)
                if key != "full_addr":
                    row.append(entry)
                    continue
                else:
                    ap = address_parser(entry)
                    for af in ADDR_FIELD_LABEL:
                        if ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                            ind = list(map(operator.itemgetter(1), ap)).index(ADDR_LABEL_TO_POSTAL[af])
                            row.append(ap[ind][0])
                        else:
                            row.append("")
                    continue
            if key == "full_addr":
                entry = _quick_scrub(entity[tags[key]])
                ap = address_parser(entry)
                for af in ADDR_FIELD_LABEL:
                    if ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                        ind = list(map(operator.itemgetter(1), ap)).index(ADDR_LABEL_TO_POSTAL[af])
                        row.append(ap[ind][0])
                    else:
                        row.append("")
                continue
            # otherwise ...
            if tags[key] != 'DPIFORCE':
                subelement = element.find(tags[key])
                subel_content = _xml_empty_element_handler(subelement)
                row.append(_quick_scrub(subel_content))
            else:
                row.append(_quick_scrub(json_data['force'][key]))
        if not _isRowEmpty(row):
            cprint.writerow(row)
    csvfile.close()
    return 0, dirty_file


def csv_parse(json_data, enc, address_parser):
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
    global ADDR_FIELD_LABEL
    global ADDR_LABEL_TO_POSTAL

    tags, filename = _csv_extract_labels(json_data)
    
    # construct csv parser
    csv_file_read = open('./pddir/pp/' + filename, 'r', encoding=enc, newline='') # errors='ignore'
    cparse = csv.DictReader(csv_file_read)

    # construct csv writer to dirty
    if len(filename.split('.')) == 1:
        dirty_file = filename + ".csv"
    else:
        dirty_file = '.'.join(str(x) for x in filename.split('.')[:-1]) + "-DIRTY.csv"
    
    csv_file_write = open('./pddir/dirty/' + dirty_file, 'w')
    cprint = csv.writer(csv_file_write, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    # write the initial row which identifies each column
    first_row = [f for f in tags]
    if "full_addr" in first_row:
        ind = first_row.index("full_addr")
        first_row.pop(ind)
        for af in reversed(ADDR_FIELD_LABEL):
            first_row.insert(ind, af)
    cprint.writerow(first_row)

    try:
        for entity in cparse:
            row = []
            for key in tags:
                # if key has a JSON array as a value
                if isinstance(tags[key], list) and key not in FORCE_LABEL:
                    count = 0
                    entry = ''
                    for i in tags[key]:
                        count += 1
                        if count == len(tags[key]):
                            entry += entity[i]
                        else:
                            entry += entity[i] + ' '
                    entry = _quick_scrub(entry)
                    # if key is full_addr and a JSON array
                    if key != "full_addr":
                        row.append(entry)
                        continue
                    else:
                        ap = address_parser(entry)
                        for af in ADDR_FIELD_LABEL:
                            if ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                                ind = list(map(operator.itemgetter(1), ap)).index(ADDR_LABEL_TO_POSTAL[af])
                                row.append(ap[ind][0])
                            else:
                                row.append("")
                        continue
                if key == "full_addr" and not isinstance(entity[tags[key]], type(None)):
                    entry = _quick_scrub(entity[tags[key]])
                    ap = address_parser(entry)
                    for af in ADDR_FIELD_LABEL:
                        if ADDR_LABEL_TO_POSTAL[af] in [x[1] for x in ap]:
                            ind = list(map(operator.itemgetter(1), ap)).index(ADDR_LABEL_TO_POSTAL[af])
                            row.append(ap[ind][0])
                        else:
                            row.append("")
                    continue
                # otherwise ...
                if tags[key] != 'DPIFORCE':
                    entry = _quick_scrub(entity[tags[key]])
                else:
                    entry = _quick_scrub(json_data['force'][key])
                row.append(entry)
            if not _isRowEmpty(row):
                cprint.writerow(row)
    except KeyError:
        print("[E] '", tags[key], "' is not a field name in the CSV file.", sep='')
        # close reader / writer and delete the partially written data file
        csv_file_read.close()
        csv_file_write.close()
        return 1, dirty_file
    except:
        print("An unknown error occurred (likely a row has less columns than prescribed).")
        # close reader / writer and delete the partially written data file
        csv_file_read.close()
        csv_file_write.close()
        return 1, dirty_file
    
    # success
    csv_file_read.close()
    csv_file_write.close()
    return 0, dirty_file



def blank_fill(fpath):
    global _FIELD_LABEL
    LABELS = [i for i in _FIELD_LABEL if i != "full_addr"]

    comp_fpath = fpath + ".complete"

    # open files for read and writing
    f = open(fpath, 'r')
    blank_fill_f = open(comp_fpath, 'w')

    # initialize csv reader/writer
    rf = csv.DictReader(f)
    wf = csv.writer(blank_fill_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    wf.writerow(LABELS)

    for old_row in rf:
        row2write = []
        for col in LABELS:
            if col not in old_row:
                row2write.append("")
            else:
                row2write.append(old_row[col])
        wf.writerow(row2write)

    blank_fill_f.close()
    f.close()


def _quick_scrub(entry):
    if isinstance(entry, bytes):
        entry = entry.decode()
    # remove [:space:] char class
    #
    # since this includes removal of newlines, the next regexps are safe and
    # do not require the "DOTALL" flag
    entry = re.sub(r"\s+", " ", entry)
    # remove spaces occuring at the beginning and end of an entry
    entry = re.sub(r"^\s+([^\s].+)", r"\1", entry)
    entry = re.sub(r"(.+[^\s])\s+$", r"\1", entry)
    entry = re.sub(r"^\s+$", "", entry)
    # DEBUG -- --
    # add regex to handle " entries " like this (remove side spaces)
    
    # make entries lowercase
    entry = entry.lower()
    return entry


def pp_format_correction(fname,enc):
    raw = open('./pddir/raw/' + fname, 'r', encoding=enc)
    pp = open('./pddir/pp/' + fname, 'w')

    reader = csv.reader(raw)
    writer = csv.writer(pp)

    flag = False
    size = 0
    for row in reader:
        if flag == True:
            while len(row) < size:
                row.append("")
            writer.writerow(row)
        else:
            size = len(row)
            flag = True
            writer.writerow(row)
        
def _isRowEmpty(r):
    for e in r:
        if e != "":
            return False
    return True
