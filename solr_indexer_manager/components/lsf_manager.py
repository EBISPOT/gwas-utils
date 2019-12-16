from subprocess import Popen, PIPE
import re
from collections import OrderedDict

class LSF_manager(object):
    
    jobs = []
    
    submitCommand = 'bsub'
    
    def __init__(self, queue = None, memory = 2000, cpus = 1, job_prefix = 'job', 
                 workingDir = '.', notify = None, job_group = None):
        
        # compile bsub parameters:
        self.bsub_parameters = OrderedDict({
                '-M' : str(memory),
                '-n' : cpus,
                '-R' : "select[mem>{}] rusage[mem={}]".format(memory, memory),
                '-J' : job_prefix,
                '-o' : job_prefix + '.o',
                '-e' : job_prefix + '.e',
        })
            
        # Add other variables:
        if notify:
            self.bsub_parameters['-N'] = notify
            
        if queue:
            self.bsub_parameters['-q'] = queue
            
        if job_group:
            self.bsub_parameters['-g'] = job_group

        # Store other parameters:
        self.workingDir = workingDir
        self.job_prefix = job_prefix
        
    def submit_job(self, command, workingDir = None, jobname = None):
        '''
        This method accepts a job and compiles into a submittable bsub command. And tries to submit.
        '''
        
        # Generate individual job description:
        command_parameters = self.bsub_parameters.copy()
        
        # Update job name if provided:
        if jobname:
            command_parameters['-J'] = jobname
            command_parameters['-o'] = jobname + '.o'
            command_parameters['-e'] = jobname + '.e'
        
        # Compile bjob:
        command_array = ['bsub']
        [command_array.extend([k,v]) for k,v in command_parameters.items()]
        command_array.append(command)
        
        # Update working directory:
        if not workingDir:
            workingDir = self.workingDir
        
        # Submit job to LSF:
        x = Popen(command_array ,stdout=PIPE, stderr=PIPE, cwd=workingDir)

        # Parse output:
        output = x.communicate()
        stdout = output[0]
        stderr = output[1]

        if stderr:
            print('[Error] Failure when submitting job:\n {}'.format(stderr))
            return(1)

        m = re.search('(\d+)', str(stdout))
        jobID = m.group(0)
        print('[Info] Job has been successfully submitted. Job ID: {}'.format(jobID))
   
        # Adding job to variable:
        self.jobs.append({
                'job_id'   : jobID,
                'status'   : 'submitted.',
                'command'  : command,
                'working_dir' : workingDir, 
                'job_name' : jobname
            })

    def check_job(self,jobID):
        x = Popen(['bjobs', '-a', jobID], stdout=PIPE, stderr=PIPE)
        y = Popen(['tail', '-n+2'], stdin=x.stdout, stdout=PIPE)
        x.stdout.close()
        
        output = y.communicate()
        stdout = str(output[0])
        
        # If status is not available for the queried jobID:
        if output[1]:
            self.jobs[jobID]['status'] = None
            return(None)
        
        # Parsing status if available:
        else:
            jobStatus = stdout.split(" ")[2]
            self.jobs[jobID]['status'] = jobStatus


    def check_all_jobs(self):
        self.update_job_status()
        statuses = {}
        indices_to_delete = []
        jobIDs_to_resubmit = []
        jobIDs_to_kill = []

        ##
        ## Looping through all jobs and update statuses:
        ##
        for index,job in enumerate(self.jobs):

            # If a job was finished, we don't care:
            if job['status'] == 'DONE':
                statuses['DONE'] ++
                continue

            # Check for and record status:
            jobID = job['job_id']
            new_status = self.check_job(jobID)
            job['status'] = new_status
            statuses[new_status] ++

            # We kill and resubmit a job if the status is not DONE, RUN or PEND
            if new_status not in ['DONE', 'RUN', 'PEND']:
                indices_to_delete.append(index)
                jobIDs_to_kill.append(jobID)
                jobIDs_to_resubmit.append(jobID)
                statuses[new_status] ++ 
                print('[Warning] A job (id: {}) was found with {} status. The job is killed and re-submitted to the farm.'.format(jobID, new_status))

            if new_status == 'DONE':
                statuses['DONE'] ++
            else:
                statuses[new_status] ++
        
        ## 
        ## Print out report:
        ##
        print('[Info] Current statuses of the submitted jobs: {}'.format(','.join(['{} - {}'.format(k,v) for k,v in statuses.items()])))

        ##
        ## Delete failed jobs form list, kill the process and re-submit them:
        ##
        if indices_to_delete:
            self.jobs = [v for i,v in enumerate(self.jobs) if i not in frozenset(indices_to_delete)]

        # kill jobs:
        for jobID in jobIDs_to_kill:
            # kill job:
            self.kill_jobID(jobID)

        # re-submit command:
        for jobID in jobIDs_to_resubmit:
            job = self.jobs[jobID]
            self.submit_job(command = job['command'], workingDir = job['working_dir'], jobname = job['job_name'])


