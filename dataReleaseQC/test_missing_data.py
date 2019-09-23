## This script tests if any study or association is missing from the exported solr.
## Also checks if all the exported studies have accession ID.

import pandas as pd
import numpy as np
import argparse


# Loading custom modules
from functions import getDataFromDB
from functions import getDataFromSolr

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
    report = ("[Warning] %s studies are missing from the solr index.\n" % len(missingStudies))
    missingStudiesDf = databaseDf.loc[databaseDf.ACCESSION_ID.isin(missingStudies)]
    
    for pmid in missingStudiesDf.PUBMED_ID.unique():
        report += ("[Warning] From publication with PMID %s, the following studies are missing: %s\n" %(
            pmid, ",".join(missingStudiesDf.loc[missingStudiesDf.PUBMED_ID == pmid, 'ACCESSION_ID'])))
    return report 


if __name__ == '__main__':
    '''
    Create Solr documents for categories of interest.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(description='This script performs a data quality check on the generated solr index after the data release. The old and the new solr indices are compared with the database.')
    parser.add_argument('--newSolrAddress', type = str, help = 'The hostname and port of the new solr index.')
    parser.add_argument('--fatSolrCore', default='gwas', type = str, help = 'The core of the tested solr core. Default: gwas.')
    parser.add_argument('--releaseDB', default='spotrel', help='Release database to extract published studies. Default: spotrel.')

    args = parser.parse_args()
    newSolrAddress = args.newSolrAddress
    fatSolrCore = args.fatSolrCore
    releaseDB = args.releaseDB

    # Initializing database objects:
    relDB = getDataFromDB.getDataFromDB(instance=releaseDB)
    
    # Initializing solr objects:
    newFatSolr = getDataFromSolr.getDataFromSolr(solrAddress=newSolrAddress, core=fatSolrCore)

    # Extracting studies:
    newFatSolrStudies = newFatSolr.getStudies()
    relDbStudies = relDB.getStudy()

    # Get number of studies from db and solr
    solrStudyCount = len(newFatSolrStudies)
    dbStudyCount = len(relDbStudies)

    # Get number of associations db and solr
    solrAssocCount = newFatSolr.getAssociationCount()
    dbAssocCount = relDB.getAssocCount()

    # Set exit code:
    exitCode = 0

    # Check if the association counts are the same:
    if solrAssocCount == dbAssocCount:
        print('[Info] Association count ({}) in solr and release database matches.'.foramt(dbAssocCount))
    else:
        print('[Warning] Association count does not match: {} in the release db vs. {} in the solr.'.format(dbAssocCount, solrAssocCount))
        exitCode += 1

    # Check if the study counts are matching:
    if solrStudyCount == dbStudyCount:
        print('[Info] Study count ({}) in solr and the release db matches.'.format(dbStudyCount))
    else:
        print('[Warning] Study count does not match: {} in the release db vs. {} in the solr.'.format(dbStudyCount, solrStudyCount))
        exitCode += 1

        # Get studies that are missing from the solr index:
        missingStudies = reportSolrVsDatabase(solrDf=newFatSolrStudies, databaseDf=relDbStudies)
        print(missingStudies)

    # Report if all looks good:
    if exitCode == 0:
        print('[Info] All tests successfully passed.')

    quit(exitCode)
