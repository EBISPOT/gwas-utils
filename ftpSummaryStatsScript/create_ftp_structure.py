#summary_statistics
#+-- gcst001-gcst002
#|   +-- gcst001
#|   +-- gcst002
#+-- gcst003-gcst004
#|   +-- gcst003
#|   +-- gcst004
#+-- gcst005-gcst006
#|   +-- gcst005
#+-- gcst...(left to preserve paths)
#+-- author_pmid_gcst...(left to preserve paths)

import os
import glob
import re
import numpy as np
import shutil
import argparse


range_size = 1000


def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1])
    floor = int(np.fix(number_part / range_size) * range_size) + 1
    upper = floor + (range_size -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor).zfill(6), u=str(upper).zfill(6))
    return range_str

def get_study_entries(pattern):
    dir_list = glob.glob(pattern)
    filtered_list = [d for d in dir_list if "-GCST" not in d]
    return filtered_list
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='Full path to ftp directory containing sumstats.')
    parser.add_argument('--pattern', type=str, help='Pattern for the glob matching - put this in quotes', default='*GCST*')
    parser.add_argument('--test', action='store_true', help='If test run is specified, nothing is actually done.')
    args = parser.parse_args()
    
    ftp_base = args.dir

    # change directory (symlinks will need to be relative, not absolute)
    os.chdir(ftp_base)
    # get gcst
    sumstats = get_study_entries(args.pattern)
    for f in sumstats:
        print("======== processing... ========")
        print(f)
        gcst = None
        gcst_regex = re.search(r'GCST[0-9]+', f)
        gcst = gcst_regex.group(0) if gcst_regex else None
        if gcst:
            print(gcst)
            gcst_range = get_gcst_range(gcst)
            new_dir = os.path.join(gcst_range, gcst)
            # move dir
            # f is symlink
            if os.path.islink(f):
                print("{} is a symlink. Ignoring it.".format(f))
            # new_dir exists but f is pmid
            elif os.path.exists(new_dir) and "_GCST" in f:
                print("New dir exists. Move {} --> {}".format(f, new_dir))
                print("create symlink: {}".format(f))
                if args.test is False:
                    shutil.rmtree(new_dir)
                    shutil.move(f, new_dir)
                    # create symlink
                    os.symlink(new_dir, f, target_is_directory=True)
            # new_dir doesn't exist
            elif not os.path.exists(new_dir):
                print("New dir does not exist. Move {} --> {}".format(f, new_dir))
                print("create symlink: {}".format(f))
                if args.test is False:
                    shutil.move(f, new_dir)
                    # create symlink
                    os.symlink(new_dir, f, target_is_directory=True)
            # new_dir exists but f is not pmid
            else:
                print("{} already exists, removing {} and creating symlink in place".format(new_dir, f))
                if args.test is False:
                    shutil.rmtree(f)
                    os.symlink(new_dir, f, target_is_directory=True)
        else:
            print("Couldn't find a GCST in {}".format(f))


if __name__ == '__main__':
    main()
