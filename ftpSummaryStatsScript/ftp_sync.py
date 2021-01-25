import os
import argparse
import requests
import glob
from urllib.parse import urljoin

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


    def get_staging_contents(self):
        return self._list_study_dirs(parent=self.staging_path, 
                                    pattern=self.nesting_dir_pattern)

    def get_ftp_contents(self):
        return self._list_study_dirs(parent=self.ftp_path, 
                                    pattern=self.nesting_dir_pattern)
    
    def get_curation_published_list(self):
        # First get all accessions for pubmed indexed (published-studies)
        published_studies_url = urljoin(self.api_url, "published-studies")
        resp = requests.get(published_studies_url, params={'size': self.api_page_size}).json()
        studies_to_release = [study['accession_id'] for study in resp['_embedded']['studies'] 
                              if self._published_is_true(study)]
        # and loop through pages
        for page in range(1, self._last_page(resp)):
            resp = requests.get(published_studies_url, params={'size': self.api_page_size, 'page': page}).json()
            studies_to_release.extend([study['accession_id'] for study in resp['_embedded']['studies'] 
                                       if self._published_is_true(study)])

        # Then get add accessuins for non-pubmed indexed (unpublished-studies)
        unpublished_studies_url = urljoin(self.api_url, "unpublished-studies")
        resp = requests.get(unpublished_studies_url, params={'size': self.api_page_size}).json()
        last_page = resp['page']['totalPages']
        studies_to_release.extend([study['study_accession'] for study in resp['_embedded']['unpublishedStudies']])
        for page in range(1, self._last_page(resp)):
            resp = requests.get(unpublished_studies_url, params={'size': self.api_page_size, 'page': page}).json()
            studies_to_release.extend([study['study_accession'] for study in resp['_embedded']['unpublishedStudies']])
        
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
        return glob.glob(os.path.join(parent, pattern, '*/'))


    def get_sumstats_status(self):
        self.staging_studies = set(self._accessions_from_dirnames(self.get_staging_contents()))
        self.ftp_studies = set(self._accessions_from_dirnames(self.get_ftp_contents()))
        self.curation_published = set(self.get_curation_published_list())
        self.to_sync_to_ftp = (self.curation_published & self.staging_studies) - self.ftp_studies
        self.remove_from_ftp = self.ftp_studies - self.curation_published
        self.missing_from_staging = self.curation_published - self.staging_studies
        self.unexpected_on_staging = self.staging_studies - self.curation_published

    @staticmethod
    def _accessions_from_dirnames(dirnames):
        return [os.path.basename(os.path.abspath(directory)) for directory in dirnames]

    def sync_study_from_staging_to_ftp(self, study):
        self.generate_md5sum_for_study_files(study)

    @staticmethod
    def generate_md5sum_for_study_files(study):
        pass

    def remove_study_from_ftp(self, study):
        pass

    def sync_to_ftp(self):
        for study in self.to_sync_to_ftp:
            pass
        # api AND staging AND NOT ftp
        

    def remove_from_ftp(self):
        # NOT api AND ftp
        pass






def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--ftpDir', type=str, help='Path to ftp directory.')
    parser.add_argument('--apiURL', type=str, help='URL base for curation REST API')
    parser.add_argument('--test', action='store_true', default='store_false', help='If test run is specified, no release is done just send notification.')
    args = parser.parse_args()
    
    sumstats_sync = SummaryStatsSync(staging_path = args.stagingDir,
                                     ftp_path = args.ftpDir,
                                     api_url = args.apiURL
                                     )

    sumstats_sync.get_sumstats_status()
    print("Missing from ftp:")
    print(len(sumstats_sync.to_sync_to_ftp))
    print("To remove from ftp:")
    print(len(sumstats_sync.remove_from_ftp))
    print("Missing from staging:")
    print(len(sumstats_sync.missing_from_staging))
    print("Unexpected on staging:")
    print(len(sumstats_sync.unexpected_on_staging))
    


if __name__ == '__main__':
    main()
