import glob
import os
import argparse
import numpy as np


range_size = 1000


class SumStatsFTPClient:
    def __init__(self, ftp_path):
        self.ftp_path = ftp_path
        self.nesting_dir_pattern = "GCST*-GCST*"

    def get_ftp_contents(self):
        return self._list_study_dirs(parent=self.ftp_path, 
                                    pattern=self.nesting_dir_pattern)

    def ftp_study_to_path_dict(self):
        self.ftp_studies_dict = self._accessions_from_dirnames(self.get_ftp_contents())
        return self.ftp_studies_dict

    @staticmethod
    def _accessions_from_dirnames(dirnames):
        # dict of {study_accession: path}
        return {os.path.basename(directory): directory for directory in dirnames}

    @staticmethod
    def _list_study_dirs(parent, pattern):
        # parent = parent dir e.g. staging dir or ftp dir
        # pattern = globbing pattern of the child dirs
        # '*/' matches dirs within the child dirs
        # abspath is very important to make sure that parent paths resolve correctly downstream
        return glob.glob(os.path.abspath(os.path.join(parent, pattern, '*/')))


def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1])
    floor = int(np.fix(number_part / range_size) * range_size) + 1
    upper = floor + (range_size -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor).zfill(6), u=str(upper).zfill(6))
    return range_str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='Path to ftp directory containing sumstats.')
    parser.add_argument('--study_accession', type=str, help='GWAS study accession you want know the path for')
    args = parser.parse_args()

    ftp_path = None
    sumstats_client = SumStatsFTPClient(args.dir)
    study_to_path_dict = sumstats_client.ftp_study_to_path_dict()
    if args.study_accession in study_to_path_dict.keys():
        ftp_path = study_to_path_dict[args.study_accession]
    else:
        range_dir = get_gcst_range(args.study_accession)
        ftp_path = os.path.join(args.dir, range_dir, args.study_accession)
    print(ftp_path)


if __name__ == '__main__':
    main()
