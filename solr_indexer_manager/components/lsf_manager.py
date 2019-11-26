import subprocess
import os
import re
from collections import OrderedDict

class LSF_manager(object):
    
    jobs = {}
    
    submitCommand = 'bsub'
    
    def __init__(self, queue = None, memory = 2000, job_prefix = 'job', 
                 workingDir = '.', notify = None, job_group = None):
        
        # compile bsub parameters:
        self.bsub_parameters = OrderedDict({
                '-M' : str(memory),
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
            print('[Error] Submitting job failed: {}'.format(stderr))
            return(1)

        m = re.search('(\d+)', str(stdout))
        jobID = m.group(0)
        print('[Info] Job has been successfully submitted. Job ID: {}'.format(jobID))
   
        # Adding job to variable:
        self.jobs.update({
            jobID : {
                'status' : 'submitted.'
            }
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


    def generate_report(self):
        self.update_job_status()
        statuses = {}
        # Looping through all jobs and getting the statuses:
        for jobID in self.jobs.keys():
            try:
                statuses[self.jobs[jobID]['status']] += 1
            except KeyError
                statuses[self.jobs[jobID]['status']] = 1
        return statuses
        
    def update_job_status(self):
        for jobID in self.jobs.keys():
            if self.jobs[jobID]['status'] == 'DONE':
                continue

