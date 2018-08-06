# An interactive script to process data with the OpenBusinessRepository.

# Modules
import argparse
import multiprocessing
import os


# Available sources for parallelization

cmd_args = argparse.ArgumentParser(description='A command-line interactive tool with the OBR.')
cmd_args.add_argument('-p', '--ignore-proc', action='store_true', default=False, \
                      help='check source files without processing data')
cmd_args.add_argument('-u', '--ignore-url', action='store_true', default=False, \
                      help='ignore "url" entries from source files')
cmd_args.add_argument('-j', '--jobs', action='store', default=1, type=int, metavar='N', \
                      help='run at most N jobs asynchronously')
cmd_args.add_argument('--log', action='store', default="pdlog.txt", type=str, \
                      metavar='FILE', help='log output to FILE')
cmd_args.add_argument('SOURCE', nargs='+', help='path to source file')

args = cmd_args.parse_args()

# get absolute paths
for i in range(0,len(args.SOURCE)):
    args.SOURCE[i] = os.path.abspath(args.SOURCE[i])
    
# change directory after adjusting paths
os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.chdir('..')

# DEBUG
print(args)

# DEBUG
# check validity of arguments (e.g. jobs is a positive number, prevent overwriting of specific
# log file, etc.
# ----- here -------

if input('Process data? (y:yes / *:exit): ') != 'y':
    print("Exiting.")
    exit(0)

print("Loading required modules...")
from postal.parser import parse_address
from process import process

# DEBUG
# trap?
# ------ here ------


if __name__ == '__main__':
    with multiprocessing.Pool(processes=args.jobs) as pool:
        # pool function calls of process.py here
        jobs = []
        for source in args.SOURCE:
            jobs.append(pool.apply_async(process, (source, args.ignore_proc, args.ignore_url)))
        # wait for jobs to finish
        results = []
        for pool_proc in jobs:
            results.append(pool_proc.get())
    print(results)
