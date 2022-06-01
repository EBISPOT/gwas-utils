import argparse
from datetime import datetime
from solrWrapper import solr_wrapper
import time
import os
import json
import subprocess

# Loading components:
from solrIndexerManager.components import getUpdated
from solrIndexerManager.components import solrUpdater
from solrIndexerManager.components import lsf_manager

class IndexerManager:
    def __init__(self, 
                 newInstance=None, 
                 oldInstance=None, 
                 solrHost=None, 
                 solrPort=None, 
                 solrCore=None, 
                 wrapperScript=None, 
                 logDir=None, 
                 fullIndex=None, 
                 memory=None, 
                 job_prefix=None, 
                 job_group=None, 
                 workingDir=None, 
                 queue=None,
                 nfScriptPath=None):
        self.newInstance = newInstance
        self.oldInstance = oldInstance
        self.solrHost = solrHost
        self.solrPort = solrPort
        self.solrCore = solrCore
        self.wrapperScript = wrapperScript
        self.logDir = logDir
        self.fullIndex = fullIndex
        self.memory = memory
        self.job_prefix = job_prefix
        self.job_group = job_group
        self.workingDir = workingDir
        self.queue = queue
        self.db_updates = None
        self.nfScriptPath = nfScriptPath
        self.job_file = None
        

    def job_generator(self):
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
        jobs = {pmid : '{} -d -e -p {}'.format(self.wrapperScript, pmid) for x in self.db_updates.values() for pmid in x if pmid != '*'}
        # Indexing job to generate disease trait and efo trait documents:
        jobs['efo_traits'] = '{} -a -s -d '.format(self.wrapperScript)
        jobs['disease_traits'] = '{} -a -s -e '.format(self.wrapperScript)
        return jobs


    def get_database_updates(self):
        # Determine updates by comparing old and new database instances:
        new_table = getUpdated.get_studies(self.newInstance)
        # The update object is generated depending on if the flag is enabled or not:
        if self.fullIndex:
            db_updates = {
                "added": new_table.PUBMED_ID.unique().tolist(),  # As if all publications in the new table was newly added
                "removed": ['*'],  # As if all publications were removed.
                "updated": []
            }
        else:
            old_table = getUpdated.get_studies(self.oldInstance)
            db_updates = getUpdated.get_db_updates(old_table, new_table)
        return db_updates
    
    def set_database_updates(self, db_updates):
        self.db_updates = db_updates

    def generate_job_list_file(self):
        job_map = self.job_generator()
        self.job_file = os.path.join(self.logDir, 'job_map.csv')
        with open(self.job_file, 'w') as f:
            for k, v in job_map.items():
                s = ",".join([k, v]) + "\n"
                f.write(s)
                
    def prepare_solr(self):
        # Instantiate solr object:
        solr_object = solr_wrapper.solrWrapper(host=self.solrHost, port=self.solrPort, core=self.solrCore)
        # Removed associations and studies for all updated/deleted studies + removing all trait documents:
        solrUpdater.removeUpdatedSolrData(solr_object, self.db_updates)
        
    def run_indexer(self):
        nextflow_cmd = """
                       nextflow {nf} --job_map_file {jm}
                       """.format(nf=self.nfScriptPath, jm=self.job_file)
        print("Running nextflow: {}".format(nextflow_cmd))
        subproc_cmd = nextflow_cmd.split()
        process = subprocess.run(subproc_cmd)
        print(process.stdout)


#def manage_lsf_jobs(job_map, workingDir):
#    '''
#    This function handles the lsf jobs. Monitors their progression and decides when to exit and how.... boy it needs to be improved.
#    '''
#
#    # Hardcoded variables:
#    memoryLimit = 8000
#    jobPrefix = 'solr_indexing'
#    jobGroup = '/gwas_catalog/solr_indexer'
#    queue = 'production'
#
#    # Initialize lsf object:
#    LSF_obj = lsf_manager.LSF_manager(memory=memoryLimit, job_prefix=jobPrefix, job_group=jobGroup, workingDir=workingDir, queue=queue)
#
#    # Looping though all jobs:
#    folder_index = 0
#
#    # Looping through all the jobs, create separate folders and submit each to the farm:
#    for job_ID, job in job_list.items():
#        try:
#            os.mkdir('{}/{}'.format(workingDir, job_ID))
#        except FileExistsError:
#            print('[Warning] folder already exists: {}/{}'.format(workingDir, job_ID))
#
#        # Submit job to farm:
#        LSF_obj.submit_job(job, workingDir='{}/{}'.format(workingDir, job_ID), jobname = job_ID)
#
#    # Wait until all jobs are finished or terminated:
#    while True:
#        report = LSF_obj.generate_report()
#
#        print('[Info] Checking statuses of the submitted jobs at: {:%b %d %H:%M}'.format(datetime.now()))
#        for status, count in report.items():
#            print("\t{}: {}".format(status, count))
#
#        if 'RUN' not in report and 'PEND' not in report and 'EXIT' not in report:
#            print('[Info] No running or pending jobs were found. Exiting.')
#            break
#
#        time.sleep(600)





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
    parser.add_argument('--logFolder', help='Folder into which the log files will be generated.', default="./")
    parser.add_argument('--nfScript', help='Nextflow script path', default="solrIndexerManager/solr_indexing.nf")
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
    nfScriptPath = args.nfScript
    verbose = args.verbose

    # Parse wrapper:
    wrapperScript = args.wrapperScript

    # Parse log directory:
    logDir = args.logFolder

    manager = IndexerManager(newInstance=newInstance, 
                             oldInstance=oldInstance, 
                             solrHost=solrHost, 
                             solrPort=solrPort,
                             solrCore=solrCore, 
                             wrapperScript=wrapperScript,
                             logDir=logDir, 
                             fullIndex=fullIndex,
                             nfScriptPath=nfScriptPath)
    db_updates = manager.get_database_updates()
    manager.set_database_updates(db_updates=db_updates)
    manager.generate_job_list_file()
    manager.prepare_solr()
    manager.run_indexer()

if __name__ == '__main__':
    main()



