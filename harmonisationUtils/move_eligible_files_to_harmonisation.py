import pathlib
import sys
import requests
import os
import json
import shutil
import argparse


gwas_rest_url = "https://www.ebi.ac.uk/gwas/rest/api"


class Study:
    def __init__(self, study_id):
        self.study_id = study_id

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


def identify_files_to_harmonise(public_ftp, depo_source):
    new_studies = os.listdir(depo_source)
    to_harmonise = {}
    published_studies = [f for f in os.listdir(public_ftp) if not f.startswith("GCST")] 
    for f in published_studies:
        if f.split("_")[-1] in new_studies:
            if 'harmonised' not in os.listdir(os.path.join(public_ftp, f)):
                to_harmonise[f.split("_")[-1]] = f
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
                print("Unable to generate a name for the sumstats")
                break


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-depo_source", help='The source for the submitted files', required=True)
    argparser.add_argument("-public_ftp", help='The public FTP sumstats path', required=True)
    argparser.add_argument("-to_format", help='The path to the formatting directory', required=True)
    argparser.add_argument("-test", help='Test run, no moving or cleaning', action='store_true', required=False)
            
    args = argparser.parse_args()
    
    depo_source = args.depo_source
    public_ftp = args.public_ftp
    to_format = args.to_format
    test_run = args.test
    
    files = identify_files_to_harmonise(public_ftp, depo_source)
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
