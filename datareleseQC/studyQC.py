import pandas as pd
import numpy as np
import subprocess
import datetime
import argparse
import codecs


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
        return("All studies from the database was exported to the solr index.\n")
    
    # Where are the missing studies:
    missingStudies = np.setdiff1d(databaseDf.ACCESSION_ID,solrDf.accessionId)
    report = ("[Warning] %s studies are missing from the solr index.\n" % len(missingStudies))
    missingStudiesDf = databaseDf.loc[databaseDf.ACCESSION_ID.isin(missingStudies)]
    
    for pmid in missingStudiesDf.PUBMED_ID.unique():
        report += ("[Warning] From publication with PMID %s, the following studies are missing: %s\n" %(
            pmid, ",".join(missingStudiesDf.loc[missingStudiesDf.PUBMED_ID == pmid, 'ACCESSION_ID'])))
    return(report)
    

def getNewStudies(newFatStudies,oldFatStudies):
    
    newStudyAccessions = np.setdiff1d(newFatStudies.accessionId,oldFatStudies.accessionId)
    newStudyDf = newFatStudies.loc[newFatStudies.accessionId.isin(newStudyAccessions.tolist())]
    
    newStudySummary = ("[Info] In the new datarelease there are %s new publications consisting of %s new studies having %s associations." % (
          len(newStudyDf.pubmedId.unique()), len(newStudyDf), newStudyDf.associationCount.sum()))
    
    newStudyDetails = "[Info] List of new publications and studies in the release:\n"
    for pmid in newStudyDf.pubmedId.unique():
        title = newStudyDf.loc[newStudyDf.pubmedId == pmid, 'title'].tolist()[0]
        assocCnt = newStudyDf.loc[newStudyDf.pubmedId == pmid, 'associationCount'].sum()
        studyCnt = len(newStudyDf.loc[newStudyDf.pubmedId == pmid])

        newStudyDetails += ("  * Paper: \"%s...\"\n" % title[0:50])
        newStudyDetails += ("\tPubmed ID: %s\n" % pmid)
        newStudyDetails += ("\tStudy count: %s, association count: %s\n" %(studyCnt, assocCnt))
        newStudyDetails += ("\tStudies: %s\n\n" % ",".join(newStudyDf.loc[newStudyDf.pubmedId == pmid, 'accessionId'].tolist()))
     
    return({'newStudySummary' : newStudySummary, 'newStudyDetails' : newStudyDetails})
        
def printDeletedStudies(newFatStudies,oldFatStudies, dbStudies):
    deletedStudies = np.setdiff1d(oldFatStudies.accessionId,newFatStudies.accessionId)
    deletedStudiesDf = oldFatStudies.loc[oldFatStudies.accessionId.isin(deletedStudies.tolist())]
    if len(deletedStudies) == 0:
        print("[Info] In this release no studies was unpublished.")
    else:
        print("[Info] In this release %s studies were unpublished." % len(deletedStudies))
        for pmid in deletedStudiesDf.pubmedId.unique():
            print("[Info] Pmid: %s the following studies were unpublished: %s, coverig %s associations" % (
                pmid, ",".join(deletedStudiesDf.loc[deletedStudiesDf.pubmedId == pmid,'accessionId']), 
                deletedStudiesDf.loc[deletedStudiesDf.pubmedId == pmid,'associationCount'].sum()))

def reportAssocCounts(solrCount, dbCount):
    report = ''
    report += ("[Info] Number of associations in the solr: %s\n" % solrCount)
    report += ("[Info] Number of associations in release database: %s\n" % dbCount)
    
    if solrCount != dbCount:
        report += ("[Warning] Number of associations in the solr (%s) and in the database (%s) is not the same!\n" %(
            solrCount))
    return(report)

def reportUnpublishedStudies(oldFatSolrStudies, newFatSolrStudies, prodDbStudies):
    missingStudies = np.setdiff1d(oldFatSolrStudies.accessionId,newFatSolrStudies.accessionId)
    unpublishedStudies = prodDbStudies.loc[prodDbStudies.ACCESSION_ID.isin(missingStudies) & 
                                           prodDbStudies.CATALOG_UNPUBLISH_DATE.notna()]

    if len(unpublishedStudies) == 0:
        return("[Info] No studies were unpublised recently.")
    report = ''
    for index, row in unpublishedStudies.iterrows():
        report += '[Info] %s (PMID: %s) was unpublised on %s (originally publised on: %s)' %(
            row['ACCESSION_ID'], row['PUBMED_ID'], row['CATALOG_UNPUBLISH_DATE'].strftime('%Y-%m-%d'), 
            row['CATALOG_PUBLISH_DATE'].strftime('%Y-%m-%d'))
    return(report)

def sendNotification(data, email):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    filename = 'SolrQC_report_%s.txt' % today

    with codecs.open(filename, "w", "utf-8-sig") as text_file:
        # Print header:
        text_file.write("Reporting post datarelease QC.\n\n")
        text_file.write("[Info] Date: %s\n" % today)

        # Print source info:
        text_file.write("[Info] URL of the old solr index: %s\n" % data['oldSolr'])
        text_file.write("[Info] URL of the new solr index: %s\n" % data['newSolr'])
        
        # Adding space:
        text_file.write("\n\n")

        # Print missingStudyReport:
        text_file.write(reports['missingStudyReport']+"\n")
        
        # Print deletedStudies:
        text_file.write(reports['deletedStudies']+"\n\n")
        
        # Print associatinos:
        text_file.write(reports['associatinos']+"\n")
        
        # Print newStudies -> header:
        text_file.write(reports['newStudies']['newStudySummary']+"\n\n")
        
        # Print newStudies -> details:
        text_file.write(reports['newStudies']['newStudyDetails'] +"\n")
        
    a = subprocess.Popen('cat %s | mutt -s "Data release QC report - %s" -- %s' %(filename, today, emailAddress), shell=True)    
    a.communicate()


if __name__ == '__main__':
    '''
    Create Solr documents for categories of interest.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(description='This script performs a data quality check on the generated solr index after the data release. The old and the new solr indices are compared with the database.')
    parser.add_argument('--oldSolrAddress', type = str, help = 'The hostname and port of the old solr index.')
    parser.add_argument('--newSolrAddress', type = str, help = 'The hostname and port of the new solr index.')
    parser.add_argument('--fatSolrCore', default='gwas', type = str, help = 'The core of the tested solr core. Defaule: gwas.')
    parser.add_argument('--document', default='study', type = str, help = 'The document type being compared. Defaule: study.')
    parser.add_argument('--productionDB', default='spotpro', help='Production database to extract unpublished date. Default: spotpro.')
    parser.add_argument('--releaseDB', default='spotrel', help='Release database to extract published studies. Default: spotrel.')
    parser.add_argument('--emailAddress', type = str, help='Email address to which the report will be sent.')

    args = parser.parse_args()
    oldSolrAddress = args.oldSolrAddress
    newSolrAddress = args.newSolrAddress
    fatSolrCore = args.fatSolrCore
    document = args.document
    productionDB = args.productionDB
    releaseDB = args.releaseDB
    emailAddress = args.emailAddress


    ## Start QC:

    # Initializing solr objects:
    oldFatSolr = getDataFromSolr.getDataFromSolr(solrAddress=oldSolrAddress, core=fatSolrCore)
    newFatSolr = getDataFromSolr.getDataFromSolr(solrAddress=newSolrAddress, core=fatSolrCore)

    # Initializing database objects:
    prodDB = getDataFromDB.getDataFromDB(instance=productionDB)
    relDB = getDataFromDB.getDataFromDB(instance=releaseDB)

    # Extracting studies:
    newFatSolrStudies = newFatSolr.getStudies()
    oldFatSolrStudies = oldFatSolr.getStudies()
    prodDbStudies = prodDB.getStudy()
    relDbStudies = relDB.getStudy()

    # Extract associations:
    solrAssocCount = newFatSolr.getAssociationCount()
    dbAssocCount = relDB.getAssocCount()

    # Generate association report:
    reports = {
        'oldSolr' : oldSolrAddress,
        'newSolr' : newSolrAddress
    }
    reports['associatinos'] = reportAssocCounts(solrCount = solrAssocCount, dbCount = dbAssocCount)

    # Generate report on new studies: dict_keys(['newStudySummary', 'newStudyDetails'])
    reports['newStudies'] = getNewStudies(newFatSolrStudies,oldFatSolrStudies)

    # Get studies that are missing from the solr index:
    reports['missingStudyReport'] = reportSolrVsDatabase(solrDf=newFatSolrStudies, databaseDf=relDbStudies)

    # Get studies which are now unpublished:
    reports['deletedStudies'] = reportUnpublishedStudies(oldFatSolrStudies, newFatSolrStudies, prodDbStudies)

    # Compile message and send notification: 
    sendNotification(reports, emailAddress)



