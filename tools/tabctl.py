# An interactive script to process data with the OpenBusinessRepository.

# Modules
import argparse
import multiprocessing
import os
import sys
import time
import io
import opentabulate

def process(source, parse_address):
    print("DEBUG:", source.local_fname)
    prodsys = opentabulate.DataProcess(source, parse_address)
    prodsys.process()
    # DEBUG
    #prodsys.blankFill()
    

# Command line interaction
cmd_args = argparse.ArgumentParser(description='A command-line interactive tool with the OBR.')
cmd_args.add_argument('-b', '--blank-fill', action='store_true', default=False, \
                      help='append blank entries for missing source file columns')
cmd_args.add_argument('-p', '--ignore-proc', action='store_true', default=False, \
                      help='check source files without processing data')
cmd_args.add_argument('-u', '--ignore-url', action='store_true', default=False, \
                      help='ignore "url" entries from source files')
cmd_args.add_argument('-z', '--no-decompress', action='store_true', default=False, \
                      help='do not decompress files from compressed archives')
cmd_args.add_argument('--pre', action='store_true', default=False, \
                      help='(EXPERIMENTAL) allow preprocessing script to run')
cmd_args.add_argument('--post', action='store_true', default=False, \
                      help='(EXPERIMENTAL) allow postprocessing script to run')
cmd_args.add_argument('-j', '--jobs', action='store', default=1, type=int, metavar='N', \
                      help='run at most N jobs asynchronously')
cmd_args.add_argument('--log', action='store', default="pdlog.txt", type=str, \
                      metavar='FILE', help='(NOT FUNCTIONAL) log output to FILE')
cmd_args.add_argument('--initialize', action='store_true', default=False, \
                      help='create processing directories')
cmd_args.add_argument('SOURCE', nargs='*', default=None, help='path to source file')

args = cmd_args.parse_args()

# get absolute paths
for i in range(0,len(args.SOURCE)):
    args.SOURCE[i] = os.path.abspath(args.SOURCE[i])
    
# change working directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir('..')

if args.initialize == True:
    PD_TREE = ['./pddir', './pddir/raw', './pddir/dirty', './pddir/clean']
    print("Creating data processing directory tree in current working directory . . .")
    for p in PD_TREE:
        if not os.path.isdir(p):
            os.makedirs(p)
    print("Done.")
    exit(0)

if args.SOURCE == []:
    print("Error! The following arguments are required: SOURCE")
    exit(1)

if args.jobs < 1:
    print("Error! Jobs should be a positive integer.")
    exit(1)

if args.log != "pdlog.txt" and os.path.exists(args.log):
    print("Warning!", args.log, "already exists.")
    if input("Overwrite? (y:yes / *:exit): ") != 'y':
        print("Exiting.")
        exit(1)

if input('Process data? (y:yes / *:exit): ') != 'y':
    print("Exiting.")
    exit(1)

print("Logging production system output to '", args.log, "'.", sep="")

src = []
urls = []

for source in args.SOURCE:
    print("Creating source object:", source)
    srcfile = opentabulate.Source(source, args.pre, args.post, args.ignore_url, \
                         args.no_decompress, args.blank_fill)
    print("Parsing...")
    srcfile.parse()
    print("Done.")
    if 'url' not in srcfile.metadata:
        print("WARNING: This source file does not have a URL.")
    if ('url' in srcfile.metadata) and (srcfile.metadata['url'] not in urls):
        srcfile.fetch_url()
        urls.append(srcfile.metadata['url'])
    if 'compression' in srcfile.metadata:
        srcfile.archive_extraction()
    src.append(srcfile)

if args.ignore_proc == True:
    exit(0)
    
print("Beginning data processing, please standby or grab a coffee. :-)")
print("Loading address parser module...")
from postal.parser import parse_address
print("Finished loading libpostal address parser.")
print("Starting multiprocessing.Pool jobs...")

start_time = time.perf_counter()

if __name__ == '__main__':
    with multiprocessing.Pool(processes=args.jobs) as pool, open(args.log, 'w') as logger:
        # pool function calls of process.py here
        jobs = []
        for source in src:
            jobs.append(pool.apply_async(process, (source, parse_address)))
        # wait for jobs to finish
        for pool_proc in jobs:
            #logger.write(pool_proc.get())
            pool_proc.get()

end_time = time.perf_counter()            

print("Completed multiprocessing.Pool execution in", end_time - start_time, "seconds.")
print("Data processing complete.")
