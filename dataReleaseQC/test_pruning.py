import argparse

# Loading custom modules:
from dataReleaseQC.functions import getDataFromDB

def main():
    '''
    Create Solr documents for categories of interest.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(description='This script checks if the release database was properly pruned or not. If the release database contain unpruned studies, this script will exit with a non-zero exit status.')
    parser.add_argument('--databaseInstance', type = str, help = 'The nane of the checked database (default: spotrel).', default = 'spotrel')

    args = parser.parse_args()
    databaseInstance = args.databaseInstance

    # Let's retrieve data from the specified db instance:
    db_handler = getDataFromDB.getDataFromDB(instance=databaseInstance)

    # Retrieve unpublished studies:
    unpublished_df = db_handler.getUnpublished()
    published_df = db_handler.getStudy()

    # Setting exit status:
    exitCode = 0

    # If the length of the returned dataframe is not zero then exit with a non-zero exit status
    if len(unpublished_df) > 0:
        print('[Error] There are {} unpublished studies in the {} database instance. Exiting.'.format(len(unpublished_df), databaseInstance))
        exitCode += 1
    else:
        print('[Info] The release database ({}) does not contain any unpublished data. Test passing.'.format(databaseInstance))

    # If any of studies in the release database does not have accession ID. The script exits with non-zero status:
    if published_df.ACCESSION_ID.isnull().any():
        print('[Error] There are {} studies in the {} database instance without accession IDs. Exiting.'.format(len(len(published_df.loc[published_df.ACCESSION_ID.isnull()])), databaseInstance))
        exitCode += 1
    else:
        print('[Info] All studies have accession ID in the release database ({}). Test passing.'.format(databaseInstance))

    if exitCode == 0:
        print('[Info] All tests passed successfully. Exiting')

    quit(exitCode)

if __name__ == '__main__':
    main()

