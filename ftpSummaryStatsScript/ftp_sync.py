import os
import re
import argparse
import requests
import glob
import hashlib
from urllib.parse import urljoin
import subprocess
from subprocess import Popen, PIPE
from pathlib import Path
import logging
import shutil


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ftpsync.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


#import api_list # LOCAL DEVELOPING ONLY

# inputs: staging, ftp and curation api
#    --> what needs to be released to ftp? = api AND staging AND NOT ftp
#      --> sync
#    --> what needs to be removed from ftp? = NOT api AND ftp
#      --> remove - what if no
#    --> what is in staging that is not in API? = NOT api AND staging
#    --> what is in API but not in staging? = api AND NOT staging
#    --> create report about what happened


class SummaryStatsSync:
    def __init__(self, staging_path, ftp_path, api_url):
        self.staging_path = staging_path
        self.ftp_path = ftp_path
        self.api_url = api_url
        self.api_page_size = 1000 # can configure if necessary
        self.nesting_dir_pattern = "GCST*-GCST*"
        self.nesting_dir_regex = "^GCST[0-9]+-GCST[0-9]+$"


    def get_staging_contents(self):
        return self._list_study_dirs(parent=self.staging_path, 
                                    pattern=self.nesting_dir_pattern)

    def get_ftp_contents(self):
        return self._list_study_dirs(parent=self.ftp_path, 
                                    pattern=self.nesting_dir_pattern)
    
    def get_curation_published_list(self):
        # First get all accessions for pubmed indexed (published-studies)
        published_studies_url = urljoin(self.api_url, "published-studies")
        resp = requests.get(published_studies_url, 
                            params={'size': self.api_page_size}
                            ).json()
        studies = resp['_embedded']['studies']
        studies_to_release = [study['accession_id'] for study in studies 
                              if self._published_is_true(study)]
        # and loop through pages
        for page in range(1, self._last_page(resp)):
            resp = requests.get(published_studies_url, 
                                params={'size': self.api_page_size, 'page': page}
                                ).json()
            studies = resp['_embedded']['studies']
            studies_to_release.extend([study['accession_id'] for study in studies 
                                       if self._published_is_true(study)])

        # Then get add accessuins for non-pubmed indexed (unpublished-studies)
        unpublished_studies_url = urljoin(self.api_url, "unpublished-studies")
        resp = requests.get(unpublished_studies_url,
                            params={'size': self.api_page_size}
                            ).json()
        last_page = resp['page']['totalPages']
        studies = resp['_embedded']['unpublishedStudies']
        studies_to_release.extend([study['study_accession'] for study in studies])
        for page in range(1, self._last_page(resp)):
            resp = requests.get(unpublished_studies_url,
                                params={'size': self.api_page_size, 'page': page}
                                ).json()
            studies = resp['_embedded']['unpublishedStudies']        
            studies_to_release.extend([study['study_accession'] for study in studies])
        
        # remove potential duplicates...just in case ;P
        return list(set(studies_to_release))

    @staticmethod
    def _last_page(resp):
        return resp['page']['totalPages']

    @staticmethod
    def _published_is_true(study):
        if study['full_pvalue_set'] == True and study['housekeeping']['is_published'] == True:
            return True
        return False

    @staticmethod
    def _list_study_dirs(parent, pattern):
        # parent = parent dir e.g. staging dir or ftp dir
        # pattern = globbing pattern of the child dirs
        # '*/' matches dirs within the child dirs
        # abspath is very important to make sure that parent paths resolve correctly downstream
        return glob.glob(os.path.abspath(os.path.join(parent, pattern, '*/')))

    @staticmethod
    def _list_files_in_dir(directory):
        only_files = [f for f in os.listdir(directory) 
                     if os.path.isfile(os.path.join(directory, f))]
        return only_files


    def get_sumstats_status(self, get_curation_status=True):
        self.staging_studies_dict = self._accessions_from_dirnames(self.get_staging_contents())
        self.staging_studies = set(self.staging_studies_dict.keys())
        self.ftp_studies_dict = self._accessions_from_dirnames(self.get_ftp_contents())
        self.ftp_studies = set(self.ftp_studies_dict.keys())
        if get_curation_status:
            self.curation_published = set(self.get_curation_published_list())
            #self.curation_published = set(api_list.RESP) # LOCAL DEVELOPING ONLY
        self.to_sync_to_ftp = (self.curation_published & self.staging_studies) - self.ftp_studies
        self.remove_from_ftp = self.ftp_studies - self.curation_published
        self.missing_from_staging = self.curation_published - self.staging_studies
        self.unexpected_on_staging = self.staging_studies - self.curation_published
        return True

    @staticmethod
    def _accessions_from_dirnames(dirnames):
        # dict of {study_accession: path}
        return {os.path.basename(directory): directory for directory in dirnames}

    def sync_study_from_staging_to_ftp(self, study):
        self.generate_md5sum_for_study_files(study)

    def _generate_md5sums_for_contents(self, directory):
        only_files = self._list_files_in_dir(directory)
        for file in only_files:
            if 'md5' in file.lower():
                return None
        md5checksums = []
        # Loopthrough the files and calculate md5sum:
        for filename in only_files:
            with open(os.path.join(directory, filename),"rb") as f:
                file_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(8192), b''):
                    file_hash.update(chunk)
                md5checksums.append([filename, file_hash.hexdigest()])
        # Saving values into a file:
        with open(os.path.join(directory,'md5sum.txt'), 'w') as writer:
            for file in md5checksums:
                writer.write('{} {}\n'.format(file[1], file[0])) 
        

    def remove_study_from_ftp(self, study):
        path = self.ftp_studies_dict[study]
        # check the end of the path is just a studyID
        if Path(path).name != study:
            logger.error("Doesn't seem right to remove {}, so I didn't.".format(path))
            return False
        try:
            logger.info("Removing {}".format(path))
            shutil.rmtree(path, ignore_errors=True)
            logger.info("==========================================")
        except FileNotFoundError as e:
            logger.error(e)

    def move_study_from_ftp_to_staging(self, study):
        source = self.ftp_studies_dict[study]
        # make nest directory on staging if required
        pardir = Path(source).parent.name
        destdir = os.path.join(self.staging_path, pardir)
        self.make_dir(destdir)
        dest = os.path.join(destdir, study)
        logger.info("Moving {} --> {}".format(source, dest))
        self.move_dir(source, dest)
        

    def sync_to_ftp(self):
        # api AND staging AND NOT ftp
        for study in self.to_sync_to_ftp:
            logger.info("{} --> FTP".format(study))
            source = self.staging_studies_dict[study]
            self._generate_md5sums_for_contents(source)
            if self._create_pardir_on_dest(source):
                self._rsync_study_dir(source, study)
        logger.info("==========================================")

    @staticmethod
    def move_dir(source, dest):
        logger.debug("Moving {} --> {}".format(source, dest))
        shutil.move(source, dest)

    @staticmethod
    def make_dir(path):
        logger.debug("mkdir: {}".format(path))
        Path(path).mkdir(parents=True, exist_ok=True)

    def _create_pardir_on_dest(self, source):
        pardir = Path(source).parent.name
        if not re.search(self.nesting_dir_regex, pardir):
            return False
        self.destdir = os.path.join(self.ftp_path, pardir)
        self.make_dir(self.destdir)
        return True

    def _rsync_study_dir(self, source, study):
        try:
            # rsync is fussy about trailing slashes and we need them in this case.
            dest = os.path.join(self.destdir, study + "/")
            source = source + "/"
            # rsync parameters:
            # -r - recursive
            # -v - verbose
            # -h - human readable output
            # --size-only - only file size is compared, timestamp is ignored
            # --delete - delete outstanding files on the target folder
            # --exclude=harmonised - excluding harmonised folders
            # --exclude=".*" - excluding hidden files
            logger.info("Sync {} --> {}".format(source, dest))
            subprocess.call(['rsync', '-rvh','--size-only', '--delete', '--exclude=harmonised', '--exclude=.*', source, dest])
        except OSError as e:
            logger.error(e)
    
    def remove_unexepcted_from_ftp(self):
        # NOT api AND ftp
        if len(self.remove_from_ftp) > 0:
            for study in self.remove_from_ftp:
                if study in self.staging_studies:
                    self.remove_study_from_ftp(study)
                else:
                    self.move_study_from_ftp_to_staging(study)


def sendEmailReport(logs, emailAddresses):
    try:
        with open(logs, 'r') as f:
            report = f.read()
            mailBody = 'Subject: Summary Stats release report\nTo: {}\n{}'.format(emailAddresses,report)
            p = Popen(["/usr/sbin/sendmail", "-t", "-oi", emailAddresses], stdin=PIPE)
            p.communicate(mailBody.encode('utf-8'))
    except OSError as e:
        logger.error(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--ftpDir', type=str, help='Path to ftp directory.')
    parser.add_argument('--apiURL', type=str, help='URL base for curation REST API')
    parser.add_argument('--test', action='store_true', help='If test run is specified, no release is done just send notification.')
    parser.add_argument('--emailRecipient', type=str, help='Email address where the notification is sent.')
    args = parser.parse_args()
    logger.info("============ FTP sync report =============")
    sumstats_sync = SummaryStatsSync(staging_path = args.stagingDir,
                                     ftp_path = args.ftpDir,
                                     api_url = args.apiURL
                                     )
    if sumstats_sync.get_sumstats_status():
        if not args.test:
            logger.info("Sync with FTP...")
            sumstats_sync.sync_to_ftp()
            sumstats_sync.remove_unexepcted_from_ftp()
            logger.info("This is not a test.")
        else:
            logger.info("This is a test. Nothing will happen.")
    sumstats_sync.get_sumstats_status(get_curation_status=False)
    logger.info("Missing from ftp: {}".format(list(sumstats_sync.to_sync_to_ftp)))
    logger.info("==========================================")
    logger.info("Missing from staging: {}".format(list(sumstats_sync.missing_from_staging)))
    logger.info("==========================================")
    logger.info("Unexpected on staging: {}".format(list(sumstats_sync.unexpected_on_staging)))
    logger.info("==========================================")
    sendEmailReport("ftpsync.log", args.emailRecipient) 
    

if __name__ == '__main__':
    main()
