# An interactive script to process data with the OpenBusinessRepository.

# Modules
import argparse
import multiprocessing
import opentabulate
import os
import signal
import time

# process data using OpenTabulate's API
def process(source, parse_address, verbose):
    #pool_worker_id = multiprocessing.current_process().name
    prodsys = opentabulate.DataProcess(source, parse_address)
    print("[DEBUG]: Starting tabulation for '", prodsys.source.local_fname, "'", sep='')
    if prodsys.source.pre_flag:
        print("[WARNING]: Running 'preprocessData()' method due to existence of 'pre' key")
        prodsys.preprocessData()
        print("[WARNING]: Completed 'preprocessData()'")
    print("[DEBUG]: Calling 'prepareData()'")
    prodsys.prepareData()
    print("[DEBUG]: Done")
    print("[DEBUG]: Calling 'extractLabels()'")
    prodsys.extractLabels()
    print("[DEBUG]: Done")
    print("[DEBUG]: Initiating 'parse()' method...")
    prodsys.parse()
    print("[DEBUG]: Completed")
    print("[DEBUG]: Initiating 'clean()' method...")
    prodsys.clean()
    print("[DEBUG]: Completed")
    if prodsys.source.post_flag:
        print("[WARNING]: Running 'postprocessData()' due to existence of 'post' key")
        prodsys.postprocessData()
        print("[WARNING]: Completed 'postprocessData()'")
    if prodsys.source.blank_fill_flag:
        print("[DEBUG]: Running 'blankFill()' due to blank-fill flag")
        prodsys.blankFill()
        print("[DEBUG]: Completed'")
    print("[DEBUG]: Tabulating '", prodsys.source.local_fname, "' complete.", sep='')

# signal handler for log files
def set_signals(handler):
    pass # TODO

# clean up logs if they were added
"""
def log_cleanup(log_name, no_jobs):
    with open(log_name, 'w') as log_file:
        for i in range(1, no_jobs + 1):
            pw = "PoolWorker-" + str(i)
            if os.path.exists(pw + ".tmp"):
                with open(pw + ".tmp") as pw_log:
                    log_file.write(pw + ":\n")
                    log_file.write(pw_log.read())
                os.remove(pw)
"""        

# Command line interaction
cmd_args = argparse.ArgumentParser(description='OpenTabulate: a command-line data tabulation tool.')
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
cmd_args.add_argument('--log', action='store_const', const="tablog.txt", \
                      help='(NOT FUNCTIONAL) log output to tablog.txt')
cmd_args.add_argument('-v', '--verbose', action='store_true',
                      help='(NOT FUNCTIONAL) enable debug mode printing')
cmd_args.add_argument('--initialize', action='store_true', default=False, \
                      help='create processing directories')
cmd_args.add_argument('SOURCE', nargs='*', default=None, help='path to source file')

args = cmd_args.parse_args()

# get absolute paths
for i in range(0,len(args.SOURCE)):
    args.SOURCE[i] = os.path.abspath(args.SOURCE[i])
    
# change working directory of tabctl.py process
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir('..')

if args.initialize == True:
    PD_TREE = ['./pddir', './pddir/raw', './pddir/dirty', './pddir/clean']
    print("[INFO]: Creating data processing directory tree in current working directory...")
    for p in PD_TREE:
        if not os.path.isdir(p):
            os.makedirs(p)
    print("[INFO]: Created directories.")
    exit(0)

if args.SOURCE == []:
    print("[ERROR]: The following arguments are required: SOURCE", file=sys.stderr)
    exit(1)

if args.jobs < 1:
    print("[ERROR]: Jobs should be a positive integer.", file=sys.stderr)
    exit(1)

if args.log:
    print("[INFO]: Logging to file '", args.log, "' in OpenTabulate.", sep='')


if input('[PROMPT]: Process data? (y:yes / *:exit): ') != 'y':
    print("[INFO]: Exiting.")
    exit(1)

src = []
urls = []

for source in args.SOURCE:
    print("[DEBUG]: Creating source object:", source)
    srcfile = opentabulate.Source(source, args.pre, args.post, args.ignore_url, \
                         args.no_decompress, args.blank_fill)
    print("[DEBUG]: Parsing contents...")
    srcfile.parse()
    print("[DEBUG]: Passed.")
        
    if 'url' not in srcfile.metadata:
        print("[WARNING]: '", source, "' does not have a URL.", sep='')
    elif ('url' in srcfile.metadata) and (srcfile.metadata['url'] not in urls):
        srcfile.fetch_url()
        urls.append(srcfile.metadata['url'])
        
    if 'compression' in srcfile.metadata:
        srcfile.archive_extraction()

    src.append(srcfile)

if args.ignore_proc == True:
    exit(0)
    
print("[INFO]: Beginning data processing, please standby or grab a coffee. :-)")
print("[INFO]: Loading address parser module...")
from postal.parser import parse_address
print("[INFO]: Finished loading libpostal address parser.")
print("[INFO]: Starting multiprocessing.Pool jobs...")

start_time = time.perf_counter()

if __name__ == '__main__':
    with multiprocessing.Pool(processes=args.jobs) as pool:
        # pool function calls of process.py here
        jobs = []
        for source in src:
            jobs.append(pool.apply_async(process, (source, parse_address, args.verbose)))
        # wait for jobs to finish
        for pool_proc in jobs:
            pool_proc.get()

end_time = time.perf_counter()            

print("[INFO]: Completed multiprocessing.Pool execution in", end_time - start_time, "seconds.")
print("[INFO]: Data processing complete.")
