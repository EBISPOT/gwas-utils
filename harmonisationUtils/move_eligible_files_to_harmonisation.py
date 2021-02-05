import pathlib
import sys
import requests
import os
import json
import shutil
import glob
import argparse
from sumstats_file_utils import SumStatsFTPClient


gwas_rest_url = "https://www.ebi.ac.uk/gwas/rest/api"

#import api_list # LOCAL DEVELOPING ONLY


class Study:
    def __init__(self, study_id):
        self.study_id = study_id
        self.pmid = None
        self.efo = None

    def set_study_metadata(self):
        study_call = gwas_rest_url + "/studies/" + self.study_id
        get_study_resp = requests.get(study_call)
        if get_study_resp.status_code == 200:
            self.pmid = get_study_resp.json()["publicationInfo"]["pubmedId"]
            efo_call = study_call + "/efoTraits"
            get_efo_resp = requests.get(efo_call)
            if get_efo_resp.status_code == 200:
                self.efo = get_efo_resp.json()["_embedded"]["efoTraits"][0]["shortForm"]
            else:
                print("Tried to make rest call to {} - received {}".format(efo_call, get_efo_resp.status_code))
        else:
            print("Tried to make rest call to {} - received {}".format(study_call, get_study_resp.status_code))

    def generate_src_name(self, build):
        if self.pmid and self.efo:
            name = "-".join([self.pmid, self.study_id, self.efo, build])
            return name
        return None


class CurationAPIClient:
    def __init__(self, curation_API_url):
        self.api_url = curation_API_url
        self.api_page_size = 1000

    def pmid_w_sumstats_study_list(self):
        # First get all accessions for pubmed indexed (published-studies)
        published_studies_url = urljoin(self.api_url, "studies")
        resp = requests.get(published_studies_url, 
                            params={'size': self.api_page_size}
                            ).json()
        studies = resp['_embedded']['studies']
        pmid_studies_w_sumstats = [study['accession_id'] for study in studies 
                              if self._published_is_true(study)]
        # and loop through pages
        for page in range(1, self._last_page(resp)):
            resp = requests.get(published_studies_url, 
                                params={'size': self.api_page_size, 'page': page}
                                ).json()
            studies = resp['_embedded']['studies']
            pmid_studies_w_sumstats.extend([study['accession_id'] for study in studies 
                                       if self._published_is_true(study)])
        return pmid_studies_w_sumstats

    @staticmethod
    def _last_page(resp):
        return resp['page']['totalPages']

    @staticmethod
    def _published_is_true(study):
        if study['full_pvalue_set'] == True and study['housekeeping']['is_published'] == True:
            return True
        return False



def identify_files_to_harmonise(public_ftp, depo_source, curation_api_url):
    new_studies = os.listdir(depo_source)
    to_harmonise = []
    curation_client = CurationAPIClient(curation_api_url)
    published_studies = curation_client.pmid_w_sumstats_study_list()
    #published_studies = api_list.RESP # LOCAL DEVELOPING ONLY
    ftp_client = SumStatsFTPClient(public_ftp)
    ftp_study_to_path_dict = ftp_client.ftp_study_to_path_dict()
    new_and_published_studies = list(set(new_studies) & set(published_studies))
    for study in new_and_published_studies:
        study_dir = ftp_study_to_path_dict[study] if study in ftp_study_to_path_dict.keys() else None
        if study_dir:
            if 'harmonised' not in os.listdir(study_dir):
                to_harmonise.append(study)
    return to_harmonise


def move_files(to_harmonise, depo_source, to_format):
    for f in to_harmonise:
        sumstats_files = [f for f in os.listdir(os.path.join(depo_source, f)) if f.startswith("GCST")]
        if len(sumstats_files) != 1:
            print("There should be one file (and only one) that looks like a sumstast file in {}, but this is not true!".format(os.path.join(depo_source, f)))
            sys.exit()
        else:
            study = Study(f)
            sumstats_src = os.path.join(depo_source, f, sumstats_files[0])
            print("source file: {}".format(sumstats_src))
            build = "Build" + str(os.path.basename(sumstats_src).split(".")[0].split("uild")[-1][-2:])
            file_ext = "".join(pathlib.Path(sumstats_src).suffixes)
            study.set_study_metadata()
            sumstats_new_name = study.generate_src_name(build)
            if sumstats_new_name: 
                sumstats_dest = os.path.join(to_format, sumstats_new_name + file_ext)
                print("moving to {}".format(sumstats_dest))
                shutil.move(sumstats_src, sumstats_dest)
                print("clearing source files")
                parent_dir = os.path.join(depo_source, f)
                print(parent_dir)
                shutil.rmtree(parent_dir)
            else:
                print("Unable to generate a name for the sumstats: {}. Leaving it alone.".format(f))
                

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-depo_source", help='The source for the submitted files', required=True)
    argparser.add_argument("-public_ftp", help='The public FTP sumstats path', required=True)
    argparser.add_argument("-to_format", help='The path to the formatting directory', required=True)
    parser.add_argument('-apiURL', type=str, help='URL base for curation REST API')
    argparser.add_argument("-test", help='Test run, no moving or cleaning', action='store_true', required=False)
            
    args = argparser.parse_args()
    
    depo_source = args.depo_source
    public_ftp = args.public_ftp
    to_format = args.to_format
    curation_api_url = args.apiURL
    test_run = args.test
    
    files = identify_files_to_harmonise(public_ftp, depo_source, curation_api_url)
    print("Files to move:")
    for f in files:
        print(f)
    if test_run is True:
        print("This was a test run, nothing actually happened")
        pass
    else:
        move_files(files, depo_source, to_format) 


if __name__ == '__main__':
        main()
