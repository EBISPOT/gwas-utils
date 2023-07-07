import sys
import argparse
import subprocess
import yaml
from typing import List, Union, Any
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
                all_studies.extend(s.name for s in get_folder_contents(path, pattern))
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
                harmonised.extend(s.parent.name for s in get_folder_contents(path, pattern))
            self.harmonised = set(harmonised)
        return self.harmonised
    
    def metadata_file_from_study_id(self, study_id: str) -> Union[Path, None]:
        study_dir = self.get_path_for_study_dir(study_id=study_id)
        matches = get_folder_contents(parent=study_dir, pattern="GCST*-meta.yaml")
        return matches[0] if matches else None

    def get_path_for_study_dir(self, study_id: str) -> Path:
        return self.sumstats_parent_dir.joinpath(get_gcst_range(study_id), study_id)

    def _get_bins(self, pattern: str = "GCST*-GCST*") -> set:
        return set(Path(s).name for s in get_folder_contents(self.sumstats_parent_dir, pattern))
    

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
        self.harmonisation_dir: Path = harmonisation_dir
        self.ftp_dir: Path = ftp_dir
        self.fs_studies = FileSystemStudies(sumstats_parent_dir, ftp_dir)
        self.harmonised: list = []
        self.unharmonised: list = []
        self.db = SqliteClient(database=database)
         
    def update_harmonisation_queue(self) -> None:
        """Updates the harmonisation queue based on the files on the file system.
        1. check for new on staging
        2. add to db
        3. check for if in_progress are harmonise -> update 
        """
        pass
    
    def release_files_from_queue(
        self,
        studies: Union[list, None] = None,
        harmonised_only: bool = False,
        harmonisation_type: List[HarmonisationType] = [e.value for e in HarmonisationType],
        limit: Union[int, None] = 200,
        in_progress: bool = False,
        priority: int = 3
        ) -> None:
        """Releases the next batch of files from the harmonisation queue.
        This copies the files at the front of the queue to the harmonisation
        directory, so that they can be harmonised.
        1. get list
        2. copy to harmonsation dir
        3. set to in_progress
        """
        study_list = self._get_from_db(studies=studies,
                                       harmonised_only=harmonised_only,
                                       harmonisation_type=harmonisation_type,
                                       limit=limit,
                                       in_progress=in_progress,
                                       priority=priority)
        for study in study_list:
            source = self.fs_studies.get_path_for_study_dir(study.study_id)
            rsync(source=source, dest=self.harmonisation_dir, pattern="GCST*")
            study.in_progress = True
            self.db.insert_study(study=astuple(study))
            print(study)
                
    def add_studies_to_queue(
        self,
        study_ids: list,
        priority: Priority = 2,
        harmonisation_type: HarmonisationType = 'v0',
        is_harmonised: bool = False,
        in_progress: bool = False
    ) -> None:
        """Add/modify studies"""
        for study_id in study_ids:
            study = Study(
                study_id=study_id,
                priority=priority,
                harmonisation_type=harmonisation_type,
                is_harmonised=is_harmonised,
                in_progress=in_progress
                )
            self.db.insert_study(study=astuple(study))
            print(study)
    
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

    def get_studies(
        self,
        studies: Union[list, None] = None
    ) -> List[Study]:
        result = self.db.select_studies(studies=studies)
        return self._db_study_to_object(result)

    def _get_from_db(
        self,
        studies: Union[list, None] = None,
        harmonised_only: bool = False,
        harmonisation_type: List[HarmonisationType] = [e.value for e in HarmonisationType],
        limit: Union[int, None] = None,
        in_progress: bool = False,
        priority: int = 3
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
        return self._db_study_to_object(result)
    
    def _db_study_to_object(self, db_result: list) -> List[Study]:
        study_list = []
        for i in db_result:    
            study_list.append(Study(study_id=i[0],
                                 harmonisation_type=i[1],
                                 is_harmonised=i[2],
                                 in_progress=i[3],
                                 priority=i[4])
                           )
        return study_list


    def _harmonisation_type_from_metadata(self, study_id) -> HarmonisationType:
        harm_type = HarmonisationType.NOT_TO_HARMONISE
        metadata_file = self.fs_studies.metadata_file_from_study_id(study_id)
        if metadata_file:
            file_type = value_from_metadata(metadata_file=metadata_file, field="fileType")
            if file_type is not None:
                if file_type.startswith("GWAS-SSF"):
                    harm_type = HarmonisationType.GWAS_SSF_1
                elif file_type.startswith("pre-GWAS-SSF"):
                    harm_type = HarmonisationType.PRE_GWAS_SSF
        return harm_type 
    

def value_from_metadata(metadata_file: Path, field: str) -> Any:
    """Get a value from the metadata

    Arguments:
        metadata_file -- metadata Yaml file
        field -- field name to extract the value from

    Returns:
        Value or None
    """
    
    if not Path(metadata_file).exists():
        return None
    else:
        with open(metadata_file, "r") as fh:
            meta_dict = yaml.safe_load(fh)
            return meta_dict.get(field)
    
    
    
def get_folder_contents(parent: Path, pattern: str) -> List[Path]:
    """List folder contents where globbing pattern matches.

    Arguments:
        parent -- parent dir e.g. staging dir or ftp dir
        pattern -- globbing pattern 
    """
    return list(Path(parent).glob(pattern))


def rsync(source: Path, dest: Path, pattern: str = "*"):
    source_str = str(source)
    dest_str = str(dest) + "/"
    try:
        subprocess.call(['rsync',
                         '-rph',
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
    if args.action == 'refresh':
        args_ok = all([args.source_dir,
                       args.harmonisation_dir,
                       args.ftp_dir])
    if args.action == 'release':
        args_ok = all([args.source_dir,
                       args.harmonisation_dir,
                       args.number])
    if args.action == 'add':
        args_ok = all([args.source_dir,
                       args.study,
                       args.priority])
    if args.action == 'rebuild':
        args_ok = all([args.source_dir,
                       args.harmonisation_dir,
                       args.ftp_dir])
    if args.action == 'status':
        args_ok = all([args.study])
    if args.action == 'update':
        args_ok = all([args.study])
    return args_ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, choices=['refresh', 'release', 'add', 'rebuild', 'status', 'update'], 
                        help=('refresh: update the harmonisation queue with newly submitted studies; '
                              'release: release the next batch of files from the queue; '
                              'add: add a specific study to the harmonisation queue; '
                              'rebuild: rebuild the entire harmonisation queue based on the files on the file system; '
                              'status: get the status of a list of studies; '
                              'update: update a list of studies'
                              ),
                        required=True)
    parser.add_argument('--study', nargs='*', help='Specific study accession ids.', default=None)
    parser.add_argument('--priority', type=int, choices=[e.value for e in Priority], help='Set the priority for a study', default=2)
    parser.add_argument('--source_dir', type=str, help='Path to source directory.', default="./staging")
    parser.add_argument('--harmonisation_dir', type=str, help='Path to harmonisation directory.', default="./toharm")
    parser.add_argument('--ftp_dir', type=str, help='Path to ftp dir', default="./ftp")
    parser.add_argument('--number', type=int, help='Number of files to harmonise', default=200)
    parser.add_argument('--harmonisation_type', type=str, choices=[e.value for e in HarmonisationType], help='harmonisation type', default='v0')
    parser.add_argument('--is_harmonised', action="store_true", help='Is harmonised', default=False)
    parser.add_argument('--in_progress', action="store_true", help='Is in progress', default=False)
    args = parser.parse_args()
    if arg_checker(args) is False:
        sys.exit("Args not sufficient for the action")

    queuer = HarmonisationQueuer(
        sumstats_parent_dir=args.source_dir,
        harmonisation_dir=args.harmonisation_dir,
        ftp_dir=args.ftp_dir
        )
    if args.action == 'rebuild':
        queuer.rebuild_harmonisation_queue()
    if args.action == 'status':
        studies = queuer.get_studies(studies=args.study)
        for study in studies:
            print(study)
    if args.action == 'update':
        queuer.add_studies_to_queue(
            study_ids=args.study,
            priority=args.priority,
            harmonisation_type=args.harmonisation_type,
            is_harmonised=args.is_harmonised,
            in_progress=args.in_progress
            )
    if args.action == 'release':
        queuer.release_files_from_queue(studies=args.study,
                                        priority=args.priority,
                                        harmonisation_type=[args.harmonisation_type],
                                        harmonised_only=args.is_harmonised,
                                        in_progress=args.in_progress,
                                        limit=args.number)
        
        


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


