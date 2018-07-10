from urllib import request
import zipfile

def fetch(data_url, filepath):
    request.urlretrieve(data_url, filepath)

def decompress(archivepath, type):
    with ZipFile(archivepath, 'r') as myzip:
        myzip.extractall(# path #
