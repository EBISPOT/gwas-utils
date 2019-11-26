import argparse
import pandas as pd
from datetime import date
from solrWrapper import solrWrapper
import time
import os

# Loading components:
from components import wrapper_manager
from components import getUpdated
from components import solrUpdater
from components import lsf_manager


def manage_lsf_jobs(wrapper_calls, trait_calls, workingDir):
    '''
    This function handles the lsf jobs. Monitors their progression and decides when to exit and how.... boy it needs to be improved.
    '''

    # Hardcoded variables:
    memoryLimit = 2000
    jobPrefix = 'solr_indexing'
    jobGroup = '/gwas_catalog/solr_indexer'

    # Initialize lsf object:
    LSF_obj = lsf_manager.LSF_manager(memory=memoryLimit, job_prefix=jobPrefix, job_group=jobGroup, workingDir=workingDir)

    # Looping though all jobs:
    folder_index = 0
    for job in wrapper_calls + trait_calls:
        try:
            os.mkdir('{}/{}'.format(workingDir, folder_index))
        except FileExistsError:
            print('[Warning] folder already exists: {}/{}'.format(logDir, i))
            continue

        # Submit job to farm:
        LSF_obj.submit_job(job, workingDir='{}/{}'.format(workingDir, folder_index))

    # Wait until all jobs are finished:
    while True:
        report = LSF_obj.generate_report()

        print('[Info] The statuses of the submitted jobs are:')
        for status, count in report.items():
            print("\t{}: {}".format(status, count))

        if 'RUN' not in report and 'PEND' not in report:
            break

        time.sleep(1800)

    # Having this means all the jobs are finished:
    report = LSF_obj.generate_report()
    return report


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

    # Location for log files:
    parser.add_argument('--logFolder', help='Folder into which the log files will be generated.')
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

    # Parse log directory:
    logDir = args.logFolder

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

    # Submitting the jobs to the farm:
    # manage_lsf_jobs(wrapper_calls, trait_calls, logDir)

