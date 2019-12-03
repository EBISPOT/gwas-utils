import pandas as pd
from gwas_db_connect import DBConnection
from collections import OrderedDict
import argparse

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
def epmc_lookup(query_terms, query_type):
    epmcHandler = ePMC_wrapper.ePMC_wrapper()
    pubData = []

    for query_term in query_terms:
        response = epmcHandler.search(queryTerms = {query_type : query_term})
        pubData += response
    
    return( pd.DataFrame(pubData))


if __name__ == '__main__':

    # Parsing input parameter:
    parser = argparse.ArgumentParser(description='This script was written to look up publications in the GWAS Catalog database.')

    # Database related input:
    parser.add_argument('--dbInstance', help='Database instance name.')
    parser.add_argument('--pmidFile', help='Txt file with the Pubmed IDs..')

    args = parser.parse_args()

    # Parser out database instance names:
    dbInstance = args.dbInstance
    pmidFile = args.pmidFile

    # establish database connection:
    connection = DBConnection.gwasCatalogDbConnector(dbInstance)

    # Look up publications in the database:
    db_lookup_df = catalog_db_lookup(connection, PMIDs)

    # Fetch data form EuroPMC:
    epmc_lookup_df = epmc_lookup(PMIDs)

    # Pooling data together:
