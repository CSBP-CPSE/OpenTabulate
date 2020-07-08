# -*- coding: utf-8 -*-
"""
Data processing cache management module.

To avoid redundant processing, a hash of the input file and corresponding source
file is cached and used in future runs to decide whether or not the input data
will be processed. By default, no processing occurs for a given dataset if and
only if the source file and input file hashes appear in the caches.

Created and written by Maksym Neyra-Nesterenko, with support and funding from the
*Center for Special Business Projects* (CSBP) at *Statistics Canada*.
"""
import hashlib
import re
import sys
import os

class CacheManager():
    """
    Cache manager object that provides the functions to read and write to the data
    processing cache. The cache is a file with lines formatted as

        FILENAME HASH

    where the hashes are SHA256 digests in hexadecimal. The choice of using SHA256
    was purely for convenience since 'hashlib' is a built-in Python module.

    Attributes:
        regex (re.Pattern): regular expression used to parse the lines of cache
        cache (list): (sorted) list of '(filename, hash)' tuples
        cache_path (str): hard-coded cache file path
    """
    def __init__(self, cache_path):
        """
        Constructor defines the cache manager attributes.
        """
        self.regex = re.compile('(.+) (.+)\n')
        self.cache = list()
        self.cache_path = cache_path
        
        if not os.path.exists(self.cache_path):
            dir_path = os.path.dirname(self.cache_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(self.cache_path, 'w'):
                pass

    def read_cache(self):
        """
        Read and load cache file.

        Raises:
            IOError: read cache does not follow line structure defined by 'regex'
        """
        with open(self.cache_path, 'r') as cache_file:
            for line in cache_file:
                match = self.regex.match(line)
                
                if match is None:
                    raise IOError("Could not read cache, line structure is malformed")

                self.cache.append(match.groups())

        self.cache.sort(key=lambda t : t[0])

    def write_cache(self):
        """
        Commit cache changes by writing to disk.

        Raises:
            IOError: failed to write cache to disk.
        """
        os.rename(self.cache_path, self.cache_path + '.tmp')
        
        try:
            with open(self.cache_path, 'w') as cache_file:
                for filename, digest in self.cache:
                    cache_file.write(filename + ' ' + digest + '\n')
        except:
            os.remove(self.cache_path)
            os.rename(self.cache_path + '.tmp', self.cache_path)
            raise IOError("Could not write cache.")

        os.remove(self.cache_path + '.tmp')

    def query(self, filename):
        """
        Query a filename in the loaded cache. The query executes a binary search.

        Returns:
            (tuple): A 3-tuple with all 'None' or the following data
                0 - (int): cache index of data item
                1 - (str): name of item at index
                2 - (str): hash digest of item at index
        """
        a = 0                 # left endpoint index
        b = len(self.cache)-1 # right endpoint index

        while a <= b:
            m = (a+b) // 2
            if self.cache[m][0] < filename:
                a = m+1
            elif self.cache[m][0] > filename:
                b = m-1
            else:
                return m, self.cache[m][0], self.cache[m][1]

        return None, None, None

    def compute_hash(self, data_path):
        """
        Compute the SHA256 hash of input data given by 'data_path'.

        Returns:
            (str): hash digest of data
        """
        hashfunc = hashlib.sha256()
        buffer_size = 4096
        
        with open(data_path, 'rb') as data:
            while True:
                chunk = data.read(buffer_size)
                
                if not chunk:
                    break
                
                hashfunc.update(chunk)

        return hashfunc.hexdigest()

    def insert(self, filename, digest):
        """
        Insert a filename and hash digest pair into the cache. The ordering by
        filename is preserved and an existing filename will have its digest
        replaced by the input digest.
        """
        a = 0
        b = len(self.cache) - 1

        ins_idx = int() # insertion index
        found_idx = bool()

        while a <= b:
            m = (a+b) // 2
            if self.cache[m][0] < filename:
                a = m+1
                ins_idx = m+1
            elif self.cache[m][0] > filename:
                b = m-1
                ins_idx = m
            else:
                self.cache[m] = (filename, digest)
                found_idx = True
                break

        if not found_idx:
            self.cache.insert(ins_idx, (filename, digest))
 

    def flush(self):
        """
        Clear the loaded cache.
        """
        self.cache.clear()