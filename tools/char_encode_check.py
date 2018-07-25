def check(f):
    if _is_utf_8(f):
        return "utf-8"
    if _is_windows_1252(f):
        return "cp1252"
    if _is_ibm_437(f):
        return "cp437"
    

def _is_utf_8(filename):
    try:
        f = open(filename, encoding="utf-8")
        for line in f:
            pass
        return True
    except UnicodeDecodeError:
        return False

def _is_windows_1252(filename):
    try:
        f = open(filename, encoding="cp1252")
        for line in f:
            pass
        return True
    except UnicodeDecodeError:
        return False

def _is_ibm_437(filename):
    try:
        f = open(filename, encoding="cp437")
        for line in f:
            pass
        return True
    except UnicodeDecodeError:
        return False
    
