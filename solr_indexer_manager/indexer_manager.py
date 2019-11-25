import argparse
import pandas as pd
from datetime import date
from solrWrapper import solrWrapper

# Loading components:
from components import wrapper_manager
from components import getUpdated
from components import solrUpdater

if __name__ == '__main__':

    # Parsing input parameter:
    parser = argparse.ArgumentParser(description='This identifies objects that needs to be updated in the solr.')

    # Database related input:
    parser.add_argument('--newInstance', help='Database instance name with the new data.')
    parser.add_argument('--oldInstance', help='Database instance name with the old data.')

    # Solr related input:
    parser.add_argument('--solrHost', help='Solr host name eg. http://localhost.')
    parser.add_argument('--solrCore', help='Core name eg. gwas.')
    parser.add_argument('--solrPort', help='Port name on which the solr server is listening.')

    # Input related to solr indexer:
    parser.add_argument('--wrapperScript', help='Wrapper script for the solr indexer.')
    args = parser.parse_args()

    # Parser out database instance names:
    newInstance = args.newInstance
    oldInstance = args.oldInstance

    # Parse solr parameter names:
    solrHost = args.solrHost
    solrCore = args.solrCore
    solrPort = args.solrPort

    # Parse wrapper:
    wrapperScript = args.wrapperScript

    # Determine updates by comparing old and new database instances:
    old_table = getUpdated.get_studies(oldInstance)
    new_table = getUpdated.get_studies(newInstance)
    db_updates = getUpdated.get_db_updates(old_table, new_table)

    # Instantiate solr object:
    solr_object = solrWrapper(host=solrHost, port=solrPort, core=solrCore, verbose=True)
    solrUpdater.removeUpdatedSolrData(solr_object, db_updates)

    # Generate a list of jobs:
    wrapper_calls = wrapper_manager.call_generator(db_updates, wrapperScript)

    # Generate trait calls:
    trait_calls = wrapper_manager.trait_calls(wrapperScript)

    # Print reports before submit to farm:
    print('[Info] Publication chunks:')
    print('\n\t'.join(wrapper_calls))

    print('[Info] Trait chunks:')
    print('\n\t'.join(trait_calls))

