import pandas as pd
import numpy as np
import codecs
import argparse
import subprocess
import datetime

# Loading custom functions:
from solrWrapper import solr_wrapper

def send_report(email = None, outputFile = None, *argv):
    """
    If at least one missing EFO term or label mismatch we send a report
    """

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    with codecs.open(outputFile, "w", "utf-8-sig") as text_file:
        
        # Print header:
        text_file.write("GWAS Catalog release notes.\n\n")
        text_file.write("\t[Info] Date: %s\n" % today)

        # Concatenating the arguments:
        for report in argv:
            text_file.write("{}\n".format(report))
            
    a = subprocess.Popen('cat %s | mutt -s "Data release QC report - %s" -- %s' %(outputFile, today, email), shell=True)
    a.communicate()

def generate_ftp_link(row):
    ftpUrl = 'http://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics' # MengW_31482140_GCST008672
    return '{}/{}_{}_{}'.format(ftpUrl, row['author_s'].replace(" ", ""), row['pubmedId'], row['accessionId'])

def report_absolute_values(newSolrStudy_df):
    """
    This function retunrs the report string with the absolute counts:
    """    
    report  = '\t[Info] Total number of publication in this release: {}\n'.format(len(newSolrStudy_df.pubmedId.unique()))
    report += '\t[Info] Total number of studies in this release: {}\n'.format(len(newSolrStudy_df))
    report += '\t[Info] Total number of associations in this release: {}\n'.format(newSolrStudy_df.associationCount.sum())
    report += '\t[Info] Total number of studies with summary statistics: {}\n'.format(len(newSolrStudy_df.loc[newSolrStudy_df.fullPvalueSet == 1]))
    return report

def report_summary_stats(newSolrStudy_df, oldSolrStudy_df, test_type = 'new'):
    """
    This function provides report on the newly released summary statistics.
    """

    # Get newly added studies:
    newStudies_accessionIDs = np.setdiff1d(newSolrStudy_df.loc[newSolrStudy_df.fullPvalueSet == 1].accessionId,
                                           oldSolrStudy_df.loc[oldSolrStudy_df.fullPvalueSet == 1].accessionId)
    newStudies_df = newSolrStudy_df.loc[newSolrStudy_df.accessionId.isin(newStudies_accessionIDs)]
    
    if len(newStudies_df) == 0 and test_type == 'new':
        return('[Info] This time no new summary statistics were released.')
    elif len(newStudies_df) == 0 and test_type == 'retracted':
        return('[Info] In this data release no summary statistics were retracted.')

    # Generate URLs for the ftp location:
    newStudies_df['ftpLink'] = newStudies_df.apply(generate_ftp_link, axis = 1)

    # Generate report:
    if test_type == 'new':
        report = '[Info] New summary statistics for {} studies of {} publication are added to the Catalog in the current release:\n'.format(len(newStudies_df), len(newStudies_df.pubmedId.unique()))
    elif test_type == 'retracted':
        report = '[Info] In this data release summary statistics of {} studes were retracted:\n'.format(len(newStudies_df))
    
    # Generate header:
    report += '\t'.join(['*','Author','Year','Title','Journal','PMID', 'Study accessions\n'])

    # Loop through the newly added publications:
    for pmid in newStudies_df.pubmedId.unique():

        # Generate header line for the publication:
        row = newStudies_df.loc[newStudies_df.pubmedId == pmid].iloc[0]

        report += '\t'.join(['*',
                    row['author_s'], 
                    row['publicationDate'].split('-')[0],
                    row['title'],
                    row['publication'],
                    row['pubmedId'],
                    ','.join(newStudies_df.loc[ newStudies_df.pubmedId == pmid].accessionId.tolist())]
                )

        report += '\n'

    report += '\n'
    return report

def report_studies(newSolrStudy_df, oldSolrStudy_df, test_type = 'new'):
    """
    This function generates a report on the newly released studies and publications.
    """
    # Get newly added studies:
    newStudies_accessionIDs = np.setdiff1d(newSolrStudy_df.accessionId,oldSolrStudy_df.accessionId)
    newStudies_df = newSolrStudy_df.loc[newSolrStudy_df.accessionId.isin(newStudies_accessionIDs)]

    # We report if nothing new happens:
    if len(newStudies_df) == 0 and test_type == 'new':
        return('[Info] In this release no study was published.\n')
    elif len(newStudies_df) == 0 and test_type == 'retracted':
        return('[Info] In this release no study was retracted.\n')

    if test_type == 'new':
        report = '[Info] There are {} new studies of {} publications in the current release:\n'.format(len(newStudies_df), len(newStudies_df.pubmedId.unique()))
    elif test_type == 'retracted':
        report = '[Info] In this release {} studies got retracted:\n'.format(len(newStudies_df))
        
    report += '\t'.join(['*','Author', 'Year', 'Title', 'Journal', 'PMID', 'Study count', 
        'Association count', 'Study accessions\n'])

    for pmid in newStudies_df.pubmedId.unique():
        row = newStudies_df.loc[newStudies_df.pubmedId == pmid].iloc[0]
        report += '\t'.join(['*',
                row['author_s'], 
                row['publicationDate'].split('-')[0],
                row['title'],
                row['publication'],
                row['pubmedId'],
                str(len(newStudies_df.loc[newStudies_df.pubmedId == pmid])),
                str(newStudies_df.loc[newStudies_df.pubmedId == pmid].associationCount.sum()),
                ', '.join(newStudies_df.loc[newStudies_df.pubmedId == pmid].accessionId.tolist())
            ])
        report += '\n'
    
    report += '\n'

    return report


def main():
    '''
    Create Solr documents for categories of interest.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(
        description='This script generates data release report. The incremental changes are reported based on the comparison of an old and a new solr index.')
    parser.add_argument('--oldSolrAddress', type=str, help='The hostname of solr server (including http/https).')
    parser.add_argument('--oldSolrPort', type=str, help='The port name on which the solr server is listening.')
    parser.add_argument('--newSolrAddress', type=str, help='The hostname of solr server (including http/https).')
    parser.add_argument('--newSolrPort', type=str, help='The port name on which the solr server is listening.')
    parser.add_argument('--solrCore', default='gwas', type=str, help='The core of the tested solr core. Defaule: gwas.')
    parser.add_argument('--emailAddress', type=str, help='Email address to which the report will be sent.')
    parser.add_argument('--outputFile', type=str, help='Otput filename into which the report will be saved.')

    args = parser.parse_args()

    # Address for the old solr:
    oldSolrHost = args.oldSolrAddress
    oldSolrPort = args.oldSolrPort

    # Address for the new solr:
    newSolrHost = args.newSolrAddress
    newSolrPort = args.newSolrPort

    # Core name:
    solrCore = args.solrCore

    # Recipient email list:
    emails = args.emailAddress

    # Output file name:
    outputFile = args.outputFile

    # Retrieve data from the old solr:
    oldSolr = solr_wrapper.solrWrapper(oldSolrHost, oldSolrPort, solrCore, verbose=False)
    oldSolrStudy_df = oldSolr.get_study_table()

    # Retrieve data from the new solr:
    newSolr = solr_wrapper.solrWrapper(newSolrHost, newSolrPort, solrCore, verbose=False)
    newSolrStudy_df = newSolr.get_study_table()

    # Extract report for absolute values of the release:
    av_report = report_absolute_values(newSolrStudy_df)

    # Get newly added studies:
    newStudyReport = report_studies(newSolrStudy_df, oldSolrStudy_df, test_type='new')

    # Get newly added summary stats:
    newSummaryStatsReport = report_summary_stats(newSolrStudy_df, oldSolrStudy_df, test_type='new')

    # Get retracted studies:
    retractedStudyReport = report_studies(oldSolrStudy_df, newSolrStudy_df, test_type='retracted')

    # Get retracted summary stats:
    retractedSummaryStatsReport = report_summary_stats(oldSolrStudy_df, newSolrStudy_df, test_type='retracted')

    # Compiling all the reports:
    send_report(emails, outputFile, av_report, newStudyReport, newSummaryStatsReport, retractedStudyReport,
                retractedSummaryStatsReport)


if __name__ == '__main__':
    main()

