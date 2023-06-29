import sys
import argparse
import shutil
import subprocess
from typing import List, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, astuple
from harmonisationUtils.sumstats_file_utils import get_gcst_range
from harmonisationUtils.db import SqliteClient


class HarmonisationType(Enum):  
    GWAS_SSF_1 = 'v1'
    PRE_GWAS_SSF = 'v0'
    NOT_TO_HARMONISE = 'not_harm'


class Priority(Enum):
    HIGH = 1
    MED = 2
    LOW = 3


@dataclass
class Study:
    """Class for study harmonisation status."""
    study_id: str
    harmonisation_type: HarmonisationType = HarmonisationType.NOT_TO_HARMONISE.value
    is_harmonised: bool = False
    in_progress: bool = False
    priority: Priority = Priority.MED.value


class FileSystemStudies:
    def __init__(
        self,
        sumstats_parent_dir: Path,
        ftp_dir: Path
        ) -> None:
        self.sumstats_parent_dir: Path = Path(sumstats_parent_dir)
        self.ftp_dir: Path = Path(ftp_dir)
        self.all: Union[set, None] = None
        self.harmonised: Union[set, None] = None
    
    def get_all(self, pattern: str = "GCST*") -> set:
        """Get all studies. The default pattern for globing is 
        the 1000 study bins, then a wildcard to match the directory
        of the study, e.g. <sumstats parent dir>/GCST0001-GCST1000/GCST0500.

        Keyword Arguments:
            pattern -- pattern for matching (default: {"GCST*-GCST*/GCST*/"})

        Returns:
            Study accessions that have summary statistics
            directories on the file system.
        """
        all_studies = []
        if self.all is None:
            for study_bin in self._get_bins():
                path = self.sumstats_parent_dir.joinpath(study_bin)
                all_studies.extend(s.name for s in get_folder_names(path, pattern))
            self.all = set(all_studies)
        return self.all

    def get_harmonised(self, pattern: str = "GCST*/harmonised") -> set:
        """Get the studies that have harmonised directories on the public FTP.

        Keyword Arguments:
            pattern -- pattern for matching (default: {"GCST*-GCST*/GCST*/harmonised"})

        Returns:
            Study accessions
        """
        harmonised = []
        if self.harmonised is None:
            for study_bin in self._get_bins():
                path = self.ftp_dir.joinpath(study_bin)
                harmonised.extend(s.parent.name for s in get_folder_names(path, pattern))
            self.harmonised = set(harmonised)
        return self.harmonised

    def _get_bins(self, pattern: str = "GCST*-GCST*") -> set:
        return set(Path(s).name for s in get_folder_names(self.sumstats_parent_dir, pattern))
    

class HarmonisationQueuer:
    """Class for queueing summary stats files for Harmonisation."""
    def __init__(
        self,
        sumstats_parent_dir: Path = "./sumstats",
        harmonisation_dir: Path = "./harmonisation",
        ftp_dir: Path = "./ftp",
        database: Path = "hq.db"
    ) -> None:
        self.sumstats_parent_dir: Path = sumstats_parent_dir
        self.harmonisatoin_dir: Path = harmonisation_dir
        self.ftp_dir: Path = ftp_dir
        self.fs_studies = FileSystemStudies(sumstats_parent_dir, ftp_dir)
        self.harmonised: list = []
        self.unharmonised: list = []
        self.db = SqliteClient(database=database)
         
    def update_harmonisation_queue(self) -> None:
        """Updates the harmonisation queue based on the files on the file system."""
        pass
    
    def release_files_from_queue(
        self,
        studies: Union[list, None] = None,
        harmonised_only: bool = False,
        harmonisation_type: List[HarmonisationType] = [e.value for e in HarmonisationType],
        limit: Union[int, None] = 200,
        in_progress: bool = False,
        priority: List[Priority] = [e.value for e in Priority]
        ) -> None:
        """Releases the next batch of files from the harmonisation queue.
        This copies the files at the front of the queue to the harmonisation
        directory, so that they can be harmonised.
        1. get list
        2. copy to harmonsation dir
        3. set to in_progress
        """
        study_list = self._get_studies_from_db(studies=studies,
                                                 harmonised_only=harmonised_only,
                                                 harmonisation_type=harmonisation_type,
                                                 limit=limit,
                                                 in_progress=in_progress,
                                                 priority=priority)
        for study in study_list:
            source = self._get_path_for_study_dir(study.study_id)
            rsync(source=source, dest=self.harmonisatoin_dir, pattern="GCST*")
            study.in_progress = True
            self.db.insert_study(study=astuple(study))
                
    def add_studies_to_queue(
        self,
        study_ids: list,
        priority: Priority = 2,
        harmonisation_type: HarmonisationType = 'v0'
    ) -> None:
        """Add/modify studies"""
        pass
    
    def rebuild_harmonisation_queue(self) -> None:
        """Start from scratch and rebuild the entire queue.
        1. get all studies from file system
        2. get all harmonised from file system
        3. store statuses in the database
        """
        
        all_fs_studies: set = self.fs_studies.get_all()
        harmonised: list = [Study(study_id=study, harmonisation_type='v0', is_harmonised=True)
                                       for study in self.fs_studies.get_harmonised()]
        unharmonised_fs_studies = list(all_fs_studies - self.fs_studies.harmonised)
        unharmonised_fs_studies.sort(reverse=True)
        unharmonised: list = [Study(study_id=study, is_harmonised=False)
                              for study in unharmonised_fs_studies]
        studies: list = harmonised + unharmonised
        for study in studies:
            self.db.insert_study(study=astuple(study))

    def _refresh_harmonisation_queue(self) -> None:
        pass

    def _get_path_for_study_dir(self, study_id: str) -> Path:
        return self.sumstats_parent_dir.joinpath(get_gcst_range(study_id), study_id)

    def _get_studies_from_db(
        self,
        studies: Union[list, None],
        harmonised_only: bool,
        harmonisation_type: List[HarmonisationType],
        limit: Union[int, None],
        in_progress: bool,
        priority: List[Priority]
    ) -> List[Study]:
        """Get a list of studies from the db.

        Keyword Arguments:
            studies -- Specify a list of study accessions
            harmonised_only -- Get harmonised only
            limit -- number to limit by, or no limit if None 
            in_progress -- Get those that are in progress 
            priority -- Filter by priority 

        Returns:
            List of studies
        """
        result = self.db.select_by(study=studies,
                                   harmonised_only=harmonised_only,
                                   harmonisation_type=harmonisation_type,
                                   limit=limit,
                                   in_progress=in_progress,
                                   priority=priority)
        study_list = []
        for i in result:    
            study_list.append(Study(study_id=i[0],
                                 harmonisation_type=i[1],
                                 is_harmonised=i[2],
                                 in_progress=i[3],
                                 priority=i[4])
                           )
        return study_list
        
        
        
    
    def _harmonisation_type_from_metadata(self, study_id) -> HarmonisationType:
        pass
    
    
def get_folder_names(parent: Path, pattern: str) -> List[Path]:
    """List folder names

    Arguments:
        parent -- parent dir e.g. staging dir or ftp dir
        pattern -- globbing pattern of the child dirs
    """
    return list(Path(parent).glob(pattern))


def rsync(source: Path, dest: Path, pattern: str = "*"):
    source_str = str(source) + "/"
    dest_str = str(dest) + "/"
    try:
        subprocess.call(['rsync',
                         '-rpvh',
                         '--chmod=Du=rwx,Dg=rwx,Do=rx,Fu=rw,Fg=rw,Fo=r',
                         '--size-only',
                         f'--include={pattern}',
                         '--exclude=*',
                         source_str,
                         dest_str]
                        )
    except OSError as e:
        print(e)


def arg_checker(args) -> bool:
    """Check arguments are ok for the particular
    action specified.

    Arguments:
        args -- arguments

    Returns:
        True if arguments are ok.
    """
    if args.action == 'update':
        args_ok = all(args.source_dir,
                      args.harmonisation_dir,
                      args.ftp_dir)
    if args.action == 'release':
        args_ok = all(args.source_dir,
                      args.harmonisation_dir,
                      args.number)
    if args.action == 'add':
        args_ok = all(args.source_dir,
                      args.study,
                      args.priority)
    if args.action == 'rebuild':
        args_ok = all(args.source_dir,
                      args.harmonisation_dir,
                      args.ftp_dir)
    return args_ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, choices=['update', 'release', 'add', 'rebuild'], 
                        help=('update: update the harmonisation queue with newly submitted studies; '
                              'release: release the next batch of files from the queue; '
                              'add: add a specific study to the harmonisation queue; '
                              'rebuild: rebuild the entire harmonisation queue based on the files on the file system'
                              ),
                        required=True)
    parser.add_argument('--study', type=list, help='Specific study accession ids to add to the queue.')
    parser.add_argument('--priority', type=int, choices=[1,2,3], help='Set the priority for a study')
    parser.add_argument('--source_dir', type=str, help='Path to source directory.', required=True)
    parser.add_argument('--harmonisation_dir', type=str, help='Path to harmonisation directory.')
    parser.add_argument('--ftp_dir', type=str, help='Path to ftp dir')
    parser.add_argument('--number', type=int, help='Number of files to harmonise', default=200)
    args = parser.parse_args()
    if arg_checker() is False:
        sys.exit("Args not sufficient for the action")

    queuer = HarmonisationQueuer(
        sumstats_parent_dir=args.source_dir,
        harmonisation_dir=args.harmonisation_dir,
        ftp_dir=args.ftp_dir,
        number_to_queue=args.number
        )
    if args.action == 'rebuild':
        queuer.rebuild_harmonisation_queue()


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



