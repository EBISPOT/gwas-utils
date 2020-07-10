import pandas as pd
import sys
import os
import argparse
from gwas_db_connect import DBConnection
import subprocess


extractStudySql = '''SELECT DISTINCT REPLACE(A.FULLNAME_STANDARD, ' ', '') AS AUTHOR, 
                            P.PUBMED_ID, S.ACCESSION_ID
                        FROM STUDY S, PUBLICATION P, HOUSEKEEPING H, AUTHOR A 
                        WHERE S.PUBLICATION_ID = P.ID 
                            AND P.FIRST_AUTHOR_ID = A.ID 
                            AND S.HOUSEKEEPING_ID = H.ID 
                            AND S.FULL_PVALUE_SET = 1 
                            AND H.IS_PUBLISHED = 1
                            AND S.ACCESSION_ID = '{}'
                      '''

def get_list_of_prepubs_in_staging(stagingDir):
    gcst_folders = [f for f in os.listdir(stagingDir) if str(os.path.basename(f)).startswith('GCST')]
    return gcst_folders
    

def get_symlink_name(connection, gcst):
    symlink_name = None
    df = pd.read_sql(extractStudySql.format(gcst), connection)
    if len(df) == 1:
        symlink_name = "_".join(df.values[0])
    elif len(df) > 1:
        print("More than one entry for that GCST in the DB - you should check fix it: {}".format(gcst))
    else:
        print("No entry in the 'published' STUDY table for: {}".format(gcst))
    return symlink_name


def make_symlink(connection, stagingDir, database, gcst, test=False):
    symlink_name = get_symlink_name(connection, gcst)
    if symlink_name:
        symlink_with_path = os.path.join(stagingDir, symlink_name)
        folder_with_path = os.path.join(stagingDir, gcst)
        if test is True:
            print("If this wasn't a test: symlink would be made for {} --> {}".format(folder_with_path, symlink_with_path))
        else:
            try:
                subprocess.call(['ln', '-vs', folder_with_path, symlink_with_path])
            except OSError as e:
                print(e) 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--releaseDB', type=str, help='Name of the database for extracting study data.')
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--test', action='store_true', default='store_false', help='If test run is specified, no release is done just send notification.')
    args = parser.parse_args()

    database = args.releaseDB
    stagingDir = args.stagingDir
    testFlag = args.test

    db_object = DBConnection.gwasCatalogDbConnector(database)
    connection = db_object.connection

    studies = get_list_of_prepubs_in_staging(stagingDir)
    for study in studies:
        make_symlink(connection, stagingDir, database, study, testFlag)


if __name__ == '__main__':
    main()
