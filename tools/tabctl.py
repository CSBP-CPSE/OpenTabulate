# An interactive script to process data with the OpenBusinessRepository.

# Modules
import argparse
import logging
import multiprocessing
import opentabulate
import os
import signal
import sys
import time

        
# process data using OpenTabulate's API
def process(source, parse_address, verbose):
    pool_worker_id = multiprocessing.current_process().name
    prodsys = opentabulate.DataProcess(source, parse_address)
    srclog = logging.getLogger(source.local_fname)
    
    srclog.debug("Starting tabulation for '%s'" % prodsys.source.local_fname)
    if prodsys.source.pre_flag and 'pre' in source.metadata:
        srclog.warning("Running 'preprocessData()' method due to --pre flag and 'pre' key")
        prodsys.preprocessData()
        srclog.warning("Completed 'preprocessData()'")
    srclog.debug("Calling 'prepareData()'")
    prodsys.prepareData()
    srclog.debug("Done")
    srclog.debug("Calling 'extractLabels()'")
    prodsys.extractLabels()
    srclog.debug("Done")
    srclog.debug("Initiating 'parse()' method...")
    try:
        prodsys.parse()
    except:
        return 1
    srclog.debug("Completed")
    srclog.debug("Initiating 'clean()' method...")
    prodsys.clean()
    srclog.debug("Completed")
    if prodsys.source.post_flag and 'post' in source.metadata:
        srclog.warning("Running 'postprocessData()' due to --post flag and 'post' key")
        prodsys.postprocessData()
        srclog.warning("Completed 'postprocessData()'")
    if prodsys.source.blank_fill_flag:
        srclog.debug("Running 'blankFill()' due to blank-fill flag")
        prodsys.blankFill()
        srclog.debug("Completed")
    srclog.debug("Tabulating '%s' complete." % prodsys.source.local_fname)
    return 0

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
                      help='enable debug mode printing')
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
    print("Creating data processing directory tree in current working directory...")
    for p in PD_TREE:
        if not os.path.isdir(p):
            os.makedirs(p)
    print("Finished creating directories")
    exit(0)

if args.SOURCE == []:
    print("Error! The following arguments are required: SOURCE", file=sys.stderr)
    exit(1)

if args.jobs < 1:
    print("Error! Jobs should be a positive integer", file=sys.stderr)
    exit(1)

#if args.log:
#    print("[INFO]: Logging to file '", args.log, "' in OpenTabulate.", sep='')

if args.verbose:
    logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s', level=logging.DEBUG)
    print("Running in debug mode (verbose output)")
else:
    logging.basicConfig(format='[%(levelname)s] <%(name)s>: %(message)s', level=logging.WARNING)
    
if input('Process data? (enter yes in capital letters): ') != 'YES':
    print("Exiting.")
    exit(1)

src = []
urls = []

srclog = logging.getLogger('source')

for source in args.SOURCE:
    srclog.debug("Creating source object: %s" % source)
    srcfile = opentabulate.Source(source, args.pre, args.post, args.ignore_url, \
                         args.no_decompress, args.blank_fill)
    srclog.debug("Parsing contents...")
    srcfile.parse()
    srclog.debug("Passed")
        
    if 'url' not in srcfile.metadata:
        srclog.warning("'%s' does not have a URL." % source)
    elif ('url' in srcfile.metadata) and (srcfile.metadata['url'] not in urls):
        srcfile.fetch_url()
        urls.append(srcfile.metadata['url'])
        
    if 'compression' in srcfile.metadata:
        srcfile.archive_extraction()

    src.append(srcfile)

if args.ignore_proc == True:
    exit(0)

# optionally load address parser
for so in src:
    if 'full_addr' in so.metadata['info']:
        logging.info("Loading address parser module...")
        try:
            from postal.parser import parse_address
        except ImportError:
            logging.error("Failed to load address parser module")
            exit(1)
        logging.info("Finished loading libpostal address parser")
        break

print("Beginning data processing, please standby or grab a coffee. :-)")

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

print("Completed pool work in", end_time - start_time, "seconds.")
print("Data processing complete.")
