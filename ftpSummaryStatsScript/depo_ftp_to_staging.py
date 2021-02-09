import os
import time
import numpy as np
import re
import argparse
import glob
import subprocess
from pathlib import Path
import logging
import shutil


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# number of seconds since modification that a file should be left alone
# in case of latency for writing the file.

#MOD_THRESHOLD_SEC = 3600 
MOD_THRESHOLD_SEC = 3 # DEV ONLY
RANGE_SIZE = 1000
RAW_SS_SUFFIX = ".rawSS"
RAW_SS_SUFFIX_REGEX = "\.rawSS$"


def get_dirs_to_sync(source_dir):
    dirs = glob.glob(os.path.join(source_dir, 'GCST*'))
    logger.debug(dirs)
    dirs_older_than_1hr = [d for d in dirs if (time.time() - os.path.getmtime(d)) > MOD_THRESHOLD_SEC]
    return dirs_older_than_1hr

def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1]) - 1
    floor = int(np.fix(number_part / RANGE_SIZE) * RANGE_SIZE) + 1
    upper = floor + (RANGE_SIZE -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor).zfill(6), u=str(upper).zfill(6))
    return range_str    

def make_dir(path):
    logger.debug("mkdir: {}".format(path))
    Path(path).mkdir(parents=True, exist_ok=True)

def move_dir(source, dest):
    logger.debug("Moving {} --> {}".format(source, dest))
    shutil.move(source, dest)

def rename_file(old, new):
    logger.info("Renaming {} --> {}".format(old, new))
    os.rename(old, new)

def remove_raw_ss_suffix(directory):
    raw_ss_files = glob.glob(os.path.join(directory, '*' + RAW_SS_SUFFIX))
    for raw_ss in raw_ss_files:
        without_raw_ss_suffix = re.sub(RAW_SS_SUFFIX_REGEX, '', raw_ss)
        rename_file(raw_ss, without_raw_ss_suffix)

def sync_files(source_dir, staging_dir, harmonise_dir):
    dirs_to_sync = get_dirs_to_sync(source_dir)
    logger.debug(dirs_to_sync)
    for study in dirs_to_sync:
        gcst = None
        basename = os.path.basename(study)
        gcst_regex = re.search(r'GCST[0-9]+', basename)
        gcst = gcst_regex.group(0) if gcst_regex else None
        if gcst:
            logger.debug(gcst)
            gcst_range = get_gcst_range(gcst)
            gcst_range_dir = os.path.join(staging_dir, gcst_range)
            gcst_range_dir = gcst_range_dir + "/"
            make_dir(gcst_range_dir)
            logger.info("Sync {} --> {}".format(study, gcst_range_dir))
            # sync to staging
            subprocess.call(['rsync', '-prvh','--chmod=Du=rwx,Dg=rwx,Do=rx,Fu=rw,Fg=rw,Fo=r', study, gcst_range_dir])
            dest = os.path.join(gcst_range_dir, gcst)
            remove_raw_ss_suffix(dest)
            # move to harmonisation
            move_dir(study, harmonise_dir + "/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sourceDir', type=str, help='Path to source directory.')
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--harmoniseDir', type=str, help='Path to harmonisation directory')
    args = parser.parse_args()

    sync_files(source_dir=args.sourceDir, 
               staging_dir=args.stagingDir, 
               harmonise_dir=args.harmoniseDir)

        

if __name__ == '__main__':
    main()
