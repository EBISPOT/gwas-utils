## This script tests if any study or association is missing from the exported solr.
## Also checks if all the exported studies have accession ID.

import numpy as np
import argparse


# Loading custom modules
from dataReleaseQC.functions import getDataFromDB
from solrWrapper import solrWrapper


def reportSolrVsDatabase(solrDf, databaseDf):
    '''
    This function compares the study data extracted from the database with the study data extarcted from 
    the fat solr
    '''

    # If the number is matching, then it should be alright.
    if len(databaseDf.ACCESSION_ID) == len(solrDf.accessionId):
        return None
    
    # Where are the missing studies:
    missingStudies = np.setdiff1d(databaseDf.ACCESSION_ID,solrDf.accessionId)
    missingStudiesDf = databaseDf.loc[databaseDf.ACCESSION_ID.isin(missingStudies)]

    report = ("[Warning] {} studies are missing from the solr index from {} publication.\n".format(
             len(missingStudiesDf),
             len(missingStudiesDf.PUBMED_ID.unique())
        ))
    
    for pmid in missingStudiesDf.PUBMED_ID.unique():
        report += ("[Warning] From publication with PMID %s, the following studies are missing: %s\n" %(
            pmid, ",".join(missingStudiesDf.loc[missingStudiesDf.PUBMED_ID == pmid, 'ACCESSION_ID'])))
    return report 

def main():
    '''
    Create Solr documents for categories of interest.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(
        description='This script performs a data quality check on the generated solr index after the data release. The old and the new solr indices are compared with the database.')
    parser.add_argument('--solrAddress', type=str, help='The hostname of the new solr index (eg. http://localhost).')
    parser.add_argument('--solrCore', default='gwas', type=str, help='The core of the tested solr core.')
    parser.add_argument('--solrPort', default='8983', type=str, help='The port on which the solr server is listening.')
    parser.add_argument('--releaseDB', default='spotrel',
                        help='Release database to extract published studies. Default: spotrel.')

    args = parser.parse_args()
    solrAddress = args.solrAddress
    solrCore = args.solrCore
    solrPort = args.solrPort
    releaseDB = args.releaseDB

    # Initializing database objects:
    relDB = getDataFromDB.getDataFromDB(instance=releaseDB)

    # Initializing solr objects:
    solr = solrWrapper(solrAddress, solrPort, solrCore)

    # Extracting studies from solr and database:
    solrStudies = solr.get_study_table()
    relDbStudies = relDB.getStudy()

    # Get number of studies from db and solr
    solrStudyCount = len(solrStudies)
    dbStudyCount = len(relDbStudies)

    # Get number of associations db and solr
    solrAssocCount = solr.get_facets()['association']
    dbAssocCount = relDB.getAssocCount()

    # Set exit code:
    exitCode = 0

    # Check if the association counts are the same:
    if solrAssocCount == dbAssocCount:
        print('[Info] Association count ({}) in solr and release database matches.'.format(dbAssocCount))
    else:
        print(
            '[Warning] Association count does not match: {} in the release db vs. {} in the solr.'.format(dbAssocCount,
                                                                                                          solrAssocCount))
        exitCode += 1

    # Check if the study counts are matching:
    if solrStudyCount == dbStudyCount:
        print('[Info] Study count ({}) in solr and the release db matches.'.format(dbStudyCount))
    else:
        print('[Warning] Study count does not match: {} in the release db vs. {} in the solr.'.format(dbStudyCount,
                                                                                                      solrStudyCount))
        exitCode += 1

        # Get studies that are missing from the solr index:
        missingStudies = reportSolrVsDatabase(solrDf=solrStudies, databaseDf=relDbStudies)
        print(missingStudies)

    # Report if all looks good:
    if exitCode == 0:
        print('[Info] All tests successfully passed.')

    quit(exitCode)

if __name__ == '__main__':
    main()

