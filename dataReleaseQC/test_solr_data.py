import pandas as pd
import requests
import sys
import urllib.parse
import numpy as np
import dateutil.parser
import argparse
import datetime
import subprocess
import codecs

# Loading custom functions:
from solrWrapper import solrWrapper

def report_missing_EFOs(study_df):
    """
    This function matches the efo terms stored in the database with the efo terms retrieved from the database.
    There are cases when the added EFO term becasuse of some reasons cannot be retrieved from OLS.
    
    Input: study_df, pandas.DataFrame object extracted from the solr index.
    """

    # Select problematic rows where at least one of the EFO term is missing from the OLS:
    def filter_rows(row):
        
        # If the efoLink field is missing this row is problematic:
        if not isinstance(row['efoLink'], list):
            return [(uri, row['mappedLabel'][i]) for i,uri in enumerate(row['mappedUri'])]

        # If any of the stored EFO terms are not within the OLS list, return row:
        missingUri = []
        for i, mappedUri in enumerate(row['mappedUri']):
            found = 0
            for efoLink in row['efoLink']:
                if mappedUri == efoLink.split('|')[2]:
                    found = 1
            if found == 0:
                missingUri.append((mappedUri, row['mappedLabel'][i]))

        return missingUri

    # Filtering for studies with missing EFO term:
    study_df['missingUri'] = study_df.apply(filter_rows, axis = 1)
    problematicStudies = study_df.loc[study_df['missingUri'].apply(lambda x: len(x)> 0)]

    # Report if all looks good:
    if len(problematicStudies) == 0:
        return None

    # If at least one row has problematic EFO terms, we have to generate a report:
    report = '[Warning] Mapped trait terms of {} studies could not be retrieved from OLS:\n\n'.format(len(problematicStudies))
    
    missingEfos = []

    # Iterating over all studies and find if any of the uri-s are missing:
    for index, row in study_df.loc[study_df.missingUri.apply(lambda x: len(x) >0)].iterrows():
        title = row['title']
        accession = row['accessionId']
        pubmedId = row['pubmedId']

        for missingUri in row['missingUri']:
            uri = missingUri[0]
            label = missingUri[1]

            missingEfos.append({
                'uri' : uri,
                'label' : label,
                'title' : title,
                'pmid' : pubmedId,
                'accession' : accession
            })
    # Generate a nice dataframe from the missing EFOs:
    missingEfos_df = pd.DataFrame(missingEfos)
    
    for URI in missingEfos_df.uri.unique():

        # Filter for rows:
        label = missingEfos_df.loc[missingEfos_df.uri == URI].label.iloc[0]
        report += '{} ({})\n'.format(label, URI)

        # For each publications we write out the accession IDs:
        for pmid in missingEfos_df.loc[missingEfos_df.uri == URI].pmid.unique():
            report += '\t* {:.50}... (pmid: {}): {}\n'.format(missingEfos_df.loc[(missingEfos_df.uri == URI) & (missingEfos_df.pmid == pmid)].title.iloc[0],
                                               pmid,
                                              ', '.join(missingEfos_df.loc[(missingEfos_df.uri == URI) & (missingEfos_df.pmid == pmid)].accession.tolist()))
        report += '\n'
    return report

def report_efo_label_mismatch(study_df):
    """
    This function compares the efo label stored in our database against the label extracted from OLS.
    It reports each cases when the two are not the same (apart from upper/lower case mismatches).
    """

    # Iterating over the mapped terms, get the uri, look it up in the efoLink fields, and if the link matches, 
    # check the label:
    def find_unmatching_label(row):
        
        unmatchingEfo = []
        for i, uri in enumerate(row['mappedUri']):
            label = row['mappedLabel'][i]

            for efoLink in row['efoLink']:
                olsUri = efoLink.split('|')[2]
                olsLabel = efoLink.split('|')[0]

                if olsUri == uri and olsLabel.lower() != label.lower():
                    unmatchingEfo.append({'olsLabel' : olsLabel, 'dbLabel' : label, 'Uri' : uri})
                    
        # If there was no problem:
        return None if unmatchingEfo == '' else unmatchingEfo

    def report_label_mismatch(row):
        return '\n\t\'{}\' instead of \'{}\' ({})'.format(row['dbLabel'], row['olsLabel'],row['Uri'])

    unmatchingTest = study_df.loc[~study_df.efoLink.isna()].apply(find_unmatching_label, axis = 1)
    unmatchingTest = unmatchingTest.loc[unmatchingTest.apply(lambda x: len(x) == 1)]

    if len(unmatchingTest) == 0:
        return None

    report = '[Warning] EFO labels are not mathing with OLS labels for {} studies'.format(len(unmatchingTest))

    # Get dataframe out of the mis-matching labels:
    unmatchingTest_unpacked = []
    unmatchingTest.apply(lambda x: [unmatchingTest_unpacked.append(y) for y in x ])
    unmatchingTest_unpacked

    # Generate dataframe:
    unmatchingTest_df = pd.DataFrame(unmatchingTest_unpacked)
    unmatchingTest_df.loc[~unmatchingTest_df.duplicated()]

    report_list = unmatchingTest_df.loc[~unmatchingTest_df.duplicated()].apply(report_label_mismatch, axis = 1)

    if len(report_list) == 0:
        return None
    else:
        report = '[Warning] There are {} mapped trait labels from {} studies where the stored label is different from the OLS label:'.format(
            len(report_list), len(unmatchingTest_df))
        for row in report_list:
            report += row

    return report

def send_report(missingEfoTermsReport, mismatchTermsReport, email, host):
    """
    If at least one missing EFO term or label mismatch we send a report
    """

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    filename = 'SolrQC_report_{}.txt'.format(today)

    with codecs.open(filename, "w", "utf-8-sig") as text_file:
        # Print header:
        text_file.write("As part of the ongoing data release, inconsistencies in the exported solr index is reported.\n\n")
        text_file.write("[Info] Date: %s\n" % today)

        # Print source info:
        text_file.write("[Info] URL of the tested solr index: {}\n\n".format(host))

        # Print missing efo terms:
        if missingEfoTermsReport:
            text_file.write(missingEfoTermsReport)

        # Print label mismatch:
        if mismatchTermsReport:
            text_file.write(mismatchTermsReport)

    a = subprocess.Popen('cat %s | mutt -s "Data release QC report - %s" -- %s' %(filename, today, email), shell=True)
    a.communicate()

def main():
    # Commandline arguments
    parser = argparse.ArgumentParser(description='This script checks if the release database was properly pruned or not. If the release database contain unpruned studies, this script will exit with a non-zero exit status.')
    parser.add_argument('--solrHost', type = str, help = 'The host where the solr server is running (with http/https).')
    parser.add_argument('--solrPort', type = int, help = 'The port on which the solr server is running.')
    parser.add_argument('--solrCore', type = str, help = 'The name of the solr core', default = 'gwas')
    parser.add_argument('--email', type = str, help = 'Email address where the report is sent.')

    args = parser.parse_args()
    host = args.solrHost
    port = args.solrPort
    core = args.solrCore
    email = args.email

    solrObject = solrWrapper(host=host, port = port, core=core)

    # Get number of documents:
    docCount = solrObject.get_all_document_count()
    print('[Info] Number of documents: {}'.format(docCount))

    # Get fatects:
    facets = solrObject.get_facets()
    print('[Info] Facets in the core:\n\t{}'.format(',\n\t'.join(['{}:{}'.format(key, value) for key, value in facets.items()])))

    # Get a number of a single resource:
    resource = 'study'
    print('[Info] Number of {} documents in the core: {}'.format(resource, solrObject.get_resource_counts(resource)))

    # Get study table:
    study_df = solrObject.get_study_table()
    print('[Info] Number or rows in the returned study table dataframe: {}'.format(len(study_df)))

    # Generate some kind of header:
    reportHeader = ''

    # Test there was any efo term that was not in the OLS upon the data release:
    missingEfoTermsReport = report_missing_EFOs(study_df)

    # Test if any of the stored EFO labels are not the same as the labels extraced from OLS:
    mismatchTermsReport = report_efo_label_mismatch(study_df)

    # If there are missing efo terms or efo label mismatch, we send report:
    if missingEfoTermsReport or mismatchTermsReport:
        send_report(missingEfoTermsReport, mismatchTermsReport, email = email, host = '{}:{}/solr/#/{}'.format(host, port, core))


if __name__ == '__main__':
    main()
