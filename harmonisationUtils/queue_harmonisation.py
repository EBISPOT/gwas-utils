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
from enum import Enum
from dataclasses import dataclass


class HarmonisationType(Enum):
    V1: 'v1'
    V0: 'v0'
    NOT_TO_HARMONISE: 'not_harm'


class Priority(Enum):
    HIGH: 1
    MED: 2
    LOW: 3


@dataclass
class Study:
    """Class for study harmonisation status."""
    study_id: str
    harmonisation_type: HarmonisationType = 'not_harm'
    is_harmonised: bool = False
    priority: Priority = 2


class HarmonisationQueuer:
    """Class for queueing summary stats files for Harmonisation."""
    def __init__(
        self,
        sumstats_parent_dir: Path,
        harmonisation_dir: Path,
        ftp_dir: Path,
        number_to_queue: int = 200
    ) -> None:
        self.number_to_queue: int = number_to_queue
        self.sumstats_parent_dir: Path = sumstats_parent_dir
        self.harmonisatoin_dir: Path = harmonisation_dir
        self.ftp_dir: Path = ftp_dir
         
    def update_harmonisation_queue(self) -> None:
        """Updates the harmonisation queue based on the files on the file system."""
        pass
    
    def release_files_from_queue(self) -> list:
        """Releases the next batch of files from the harmonisation queue.
        This copies the files at the front of the queue to the harmonisation
        directory, so that they can be harmonised."""
        pass
    
    def _refresh_harmonisation_queue(self) -> None:
        pass

    def _copy_files_to_harmonisation_dir(self) -> None:
        pass

    def _get_path_for_study_dir(self, study_id: str) -> Path:
        pass

    def _get_study_ids_from_file_system(self, harmonised_only: bool = False) -> list:
        pass
    
    def _get_study_ids_from_db(self, harmonised_only: bool = False) -> list:
        pass
    
    def _harmonisation_type_from_metadata(self, study_id) -> HarmonisationType:
        pass
    

def arg_checker(args) -> bool:
    if args.action == 'update':
        all(args.source_dir,
            args.harmonisation_dir,
            args.ftp_dir)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, choices=['update', 'release', 'add'], required=True)
    parser.add_argument('--source_dir', type=str, help='Path to source directory.')
    parser.add_argument('--harmonisation_dir', type=str, help='Path to harmonisation directory.')
    parser.add_argument('--ftp_dir', type=str, help='Path to ftp dir')
    parser.add_argument('--number', type=int, help='Number of files to harmonise', default=200)
    args = parser.parse_args()


    queuer = HarmonisationQueuer(
        sumstats_parent_dir=args.source_dir,
        harmonisation_dir=args.harmonisation_dir,
        ftp_dir=args.ftp_dir,
        number_to_queue=args.number
        )
    queuer.queue_next_studies()


if __name__ == '__main__':
    main()



# 1. python:
# 	1. get_files_for_harmonisation(number=x)
# 			pulls out first x number of files from db
# 			copies them to harmonisation dir
# 	2. add_files_for_harmonisation(list_of_studies, add_to_start=False, queue=HarmonisationType)
# 	3. get_harmonisation_type(study) -> HarmonisationType 
# 	4. refresh_to_harmonise_list()
# 		1. identify studies that have not been harmonised











# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # number of seconds since modification that a file should be left alone
# # in case of latency for writing the file.

# MOD_THRESHOLD_SEC = 3600
# #MOD_THRESHOLD_SEC = 36 # DEV ONLY
# RANGE_SIZE = 1000


# def get_dirs_to_sync(source_dir):
#     dirs = glob.glob(os.path.join(source_dir, 'GCST*'))
#     dirs_older_than_1hr = [d for d in dirs if (time.time() - os.path.getmtime(d)) > MOD_THRESHOLD_SEC]
#     return dirs_older_than_1hr

# # find all changed files since lastrun - subtract an hour from window to allow for latency - so it's a window 1 hour back.
# cmd = ['find', '/nfs/production/parkinso/spot/gwas/prod/data/summary_statistics', '-type', 'f', '-name',
#            'GCST*.tsv*', '-newermt', '2022-06-30 23:01:59']
# j = subprocess.run(cmd, stdout=subprocess.PIPE)
# modified_files = j.stdout.decode().split()
# # modified_files is a list of files to sync to FTP, whether they exist on the FTP or not
# k = [f for f in modified_files if valid_for_harmonisation(f)]

# # valid_for_harmonisation will take a file determine if is sumstats GCST*.tsv* or YAML and based on the YAML decide check if valid, if so move to harmonise queue
# # right now, we can't do that, so instead we will check if sumstats (GCST*.tsv|csv|txt*) and check it is part of a publication, if so move to harmonise queue

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--sourceDir', type=str, help='Path to source directory.')
#     parser.add_argument('--destDir', type=str, help='Path to destination directory.')
#     parser.add_argument('--lastRun', type=str, help='Path to last run file', default='.lastrun')
#     args = parser.parse_args()

#     source_dir = args.sourceDir
#     dest_dir = args.destDir
#     last_run = args.lastRun

#     # read last run - get last run timestamp
#     # identify files for queue
#     # read yaml OR api
#     # cp file to dest
#     sync_files(source_dir=args.sourceDir,
#                staging_dir=args.stagingDir,
#                harmonise_dir=args.harmoniseDir)



