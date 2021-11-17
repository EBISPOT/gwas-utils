import argparse
from datetime import datetime
from solrWrapper import solr_wrapper
import time
import os

# Loading components:
from solrIndexerManager.components import getUpdated
from solrIndexerManager.components import solrUpdater
from solrIndexerManager.components import lsf_manager

def job_generator(db_updates, wrapper):
    """
    This function generates the jobs based on the provided wrapper script and the dictionary with the db updates.

    Return data:
    {
        ${pmid} : './${wrapper} -d -e -p ${pmid}',
        ...
        efotrait : './${wrapper} -a -s -d',
        diseasetrait : './${wrapper} -a -s -e'
    }
    """

    # Indexing jobs with associations and studies for each pubmed ID:
    jobs = {pmid : '{} -d -e -p {}'.format(wrapper, pmid) for x in db_updates.values() for pmid in x if pmid != '*'}

    # Indexing job to generate disease trait and efo trait documents:
    jobs['efo_traits'] = '{} -a -s -d '.format(wrapper)
    jobs['disease_traits'] = '{} -a -s -e '.format(wrapper)

    return jobs

def manage_lsf_jobs(job_list, workingDir):
    '''
    This function handles the lsf jobs. Monitors their progression and decides when to exit and how.... boy it needs to be improved.
    '''

    # Hardcoded variables:
    memoryLimit = 4000
    jobPrefix = 'solr_indexing'
    jobGroup = '/gwas_catalog/solr_indexer'
    queue = 'production-rh74'

    # Initialize lsf object:
    LSF_obj = lsf_manager.LSF_manager(memory=memoryLimit, job_prefix=jobPrefix, job_group=jobGroup, workingDir=workingDir, queue=queue)

    # Looping though all jobs:
    folder_index = 0

    # Looping through all the jobs, create separate folders and submit each to the farm:
    for job_ID, job in job_list.items():
        try:
            os.mkdir('{}/{}'.format(workingDir, job_ID))
        except FileExistsError:
            print('[Warning] folder already exists: {}/{}'.format(workingDir, job_ID))

        # Submit job to farm:
        LSF_obj.submit_job(job, workingDir='{}/{}'.format(workingDir, job_ID), jobname = job_ID)

    # Wait until all jobs are finished or terminated:
    while True:
        report = LSF_obj.generate_report()

        print('[Info] Checking statuses of the submitted jobs at: {:%b %d %H:%M}'.format(datetime.now()))
        for status, count in report.items():
            print("\t{}: {}".format(status, count))

        if 'RUN' not in report and 'PEND' not in report and 'EXIT' not in report:
            print('[Info] No running or pending jobs were found. Exiting.')
            break

        time.sleep(600)


def main():
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

    # Input related to solr indexer:
    parser.add_argument('--fullIndex',
                        help='Flag to indicate that the entire solr index needs to be wiped off. And the whole index is going to be re-generated.',
                        action="store_true")

    # Location for log files:
    parser.add_argument('--logFolder', help='Folder into which the log files will be generated.')

    # Print out excessive reports:
    parser.add_argument('--verbose', help='Flag to give more informative output.', action="store_true")
    args = parser.parse_args()

    # Parser out database instance names:
    newInstance = args.newInstance
    oldInstance = args.oldInstance

    # Parse solr parameter names:
    solrHost = args.solrHost
    solrCore = args.solrCore
    solrPort = args.solrPort
    fullIndex = args.fullIndex
    verbose = args.verbose

    # Parse wrapper:
    wrapperScript = args.wrapperScript

    # Parse log directory:
    logDir = args.logFolder

    # Determine updates by comparing old and new database instances:
    old_table = getUpdated.get_studies(oldInstance)
    new_table = getUpdated.get_studies(newInstance)

    # The update object is generated depending on if the flag is enabled or not:
    if fullIndex:
        db_updates = {
            "added": new_table.PUBMED_ID.unique().tolist(),  # As if all publications in the new table was newly added
            "removed": ['*'],  # As if all publications were removed.
            "updated": []
        }
    else:
        db_updates = getUpdated.get_db_updates(old_table, new_table)

    # Instantiate solr object:
    solr_object = solr_wrapper.solrWrapper(host=solrHost, port=solrPort, core=solrCore, verbose=True)

    # Removed associations and studies for all updated/deleted studies + removing all trait documents:
    solrUpdater.removeUpdatedSolrData(solr_object, db_updates)

    # Generate a list of jobs:
    joblist = job_generator(db_updates, wrapperScript)

    # Print reports before submit to farm:
    if verbose:
        print('[Info] List of jobs to be submitted to the farm:')
        print('\n\t'.join(joblist.values()))

    # Submitting the jobs to the farm:
    manage_lsf_jobs(joblist, logDir)

    # At this point there's no downstream management of the jobs.... just submit and wait.
    # we are assuming things went well. If not downstream QC measures will terminate the plan anyway.
    # Later time based on experience this can be made more sophisticated.


if __name__ == '__main__':
    main()



