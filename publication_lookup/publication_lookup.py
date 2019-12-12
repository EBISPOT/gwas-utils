import pandas as pd
from gwas_db_connect import DBConnection
from collections import OrderedDict
import argparse
import re

# Loading components:
from components import ePMC_wrapper


def catalog_db_lookup(connection, pmid_list):

    # sql to get the table with all the 
    study_lookup_sql = '''
        SELECT S.ACCESSION_ID, S.FULL_PVALUE_SET, P.PUBMED_ID
        FROM STUDY S,
            PUBLICATION P
        WHERE P.PUBMED_ID = :pmid
            AND P.ID = S.PUBLICATION_ID
    '''
    
    # Lookup collected in a list of dictionaries:
    pooled_lookup = []
    
    for pmid in pmid_list:

        df = pd.read_sql(study_lookup_sql, connection.connection, params= {'pmid' : pmid})
        
        in_catalog = True if len(df) > 0 else False 
        
        pooled_lookup.append(OrderedDict({
            'pmid' : pmid,
            'in_catalog' : in_catalog,
            'study_accession' : ','.join(df.ACCESSION_ID.tolist()),
            'summary_stats' : df.FULL_PVALUE_SET.isin(['1']).any(),
        }))

    return(pd.DataFrame(pooled_lookup))

# The epmc lookup can be done in any field:
def epmc_lookup(query_terms):
    epmcHandler = ePMC_wrapper.ePMC_wrapper(resultType = 'core')

    for query_term in query_terms:
        print(query_term)
        # Inferring query type:
        query_type = 'pmid' if re.match('^[0-9]+$',query_term) else 'title'

        # Fetch data from EuroPMC:
        epmcHandler.search(queryTerms = {query_type : query_term})

        # Extract parsed response:
        returnData = epmcHandler.parse_field()

        # Update queried fields if nothing was found:
        if returnData[query_type].tolist()[0] != query_term:
            returnData[query_type] = query_term

        # Adding rows to dataframe:
        try:
            pubData = pubData.append(returnData,sort=False, ignore_index = True)
        except:
            pubData = returnData

    # Extrat the first author:
    pubData['first_author'] = pubData.authors.apply(lambda x: x.split(',')[0] if x else None)
    pubData.drop(['authors'], axis=1)

    return(pubData)

if __name__ == '__main__':

    # Parsing input parameter:
    parser = argparse.ArgumentParser(description='This script was written to look up publications in the GWAS Catalog database.')

    # Database related input:
    parser.add_argument('--dbInstance', help='Database instance name.', type=str)
    parser.add_argument('--input', help='Txt file with query terms.', type=str)
    parser.add_argument('--output', help='tsv file to save output.', default = 'output.tsv')
    args = parser.parse_args()

    # Parse input parameters:
    dbInstance = args.dbInstance
    inputFile = args.input
    outputFile = args.output

    # Content of the input file will be stored in this array:
    input_container = []

    # Read input file:
    with open(inputFile) as f:
        for line in f:
            line = line.strip()
            input_container.append(line)

    # Print report:
    print('[Info] {} query items were read from the input file ({}).'.format(len(input_container), inputFile))

    # Fetch data form EuroPMC:
    epmc_lookup_df = epmc_lookup(input_container)
    print('[Info] {} of the queried input were found in the EPMC database.'.format(len(epmc_lookup_df.loc[~epmc_lookup_df.journal.isna()])))

    # Establish database connection:
    connection = DBConnection.gwasCatalogDbConnector(dbInstance)

    # Look up publications in the database:
    db_lookup_df = catalog_db_lookup(connection, epmc_lookup_df.pmid.tolist())
    print('[Info] {} of the queried input were found in the GWAS database.'.format(len(db_lookup_df.loc[db_lookup_df.in_catalog])))

    # Pooling data together:
    merged_df = epmc_lookup_df.merge(db_lookup_df, left_on='pmid', right_on='pmid')
    column_order = ['title', 'first_author', 'date', 'journal', 'pmid', 'c_author', 'c_orcid', 'c_email', 'in_catalog', 'study_accession', 'summary_stats']
    merged_df[column_order].to_csv(outputFile, sep = '\t', index = False)

    print('[Info] Combined table saved to {}'.format(outputFile))
