import csv
import datetime
import getopt
import json
import sys
import os
import numpy as np
import urllib.request
from collections import defaultdict


#Global variables for summary statistics FTP path
SUMSTAST_FTP_BASE_PATH = 'ftp://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/'
RANGE_SIZE = 1000

def build_ancestry_download(url, outputdir):
    #STUDY ACCESSION	FIRST AUTHOR	STAGE	NUMBER OF INDIVDUALS	BROAD ANCESTRAL CATEGORY	COUNTRY OF RECRUITMENT	ADDITONAL ANCESTRY DESCRIPTION	Founder/Genetically isolated population	Number of cases	Number of controls	Sample description	DOI
    with urllib.request.urlopen(url) as f:
        data = json.load(f)
        print(data)

        with open(outputdir + '/gwas-catalog-unpublished-ancestries-v1.0.3.tmp.tsv', 'w', newline='') as csvfile:
            fieldnames = ['STUDY ACCESSION', 'PUBMED ID', 'FIRST AUTHOR', 'DATE', 'INITIAL SAMPLE DESCRIPTION',
                          'REPLICATION SAMPLE DESCRIPTION', 'STAGE', 'NUMBER OF INDIVIDUALS',
                          'BROAD ANCESTRAL CATEGORY', 'COUNTRY OF ORIGIN', 'COUNTRY OF RECRUITMENT',
                          'ADDITIONAL ANCESTRY DESCRIPTION', 'ANCESTRY DESCRIPTOR',
                          'FOUNDER/GENETICALLY ISOLATED POPULATION',
                          'NUMBER OF CASES', 'NUMBER OF CONTROLS', 'SAMPLE DESCRIPTION', 'COHORT(S)',
                          'COHORT-SPECIFIC REFERENCE']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)
            writer.writeheader()
            for study in data:
                table = defaultdict()
                table['STUDY ACCESSION'] = study['study_accession']
                table['PUBMED ID'] = 'NA'
                if not study['body_of_work']:
                    table['FIRST AUTHOR'] = ''
                else:
                    if 'first_author' in study['body_of_work'][0]:
                        table['FIRST AUTHOR'] = study['body_of_work'][0]['first_author']
                    else:
                        table['FIRST AUTHOR'] = 'NA'
                table['DATE'] = 'not yet curated'
                table['INITIAL SAMPLE DESCRIPTION'] = 'not yet curated'
                table['REPLICATION SAMPLE DESCRIPTION'] = 'not yet curated'
                table['COHORT(S)'] = study['cohort']
                table['COHORT-SPECIFIC REFERENCE'] = study['cohort_id']
                for sample in study['unpublishedAncestries']:
                    table['STAGE'] = sample['stage']
                    table['NUMBER OF INDIVIDUALS'] = sample['sample_size']
                    table['BROAD ANCESTRAL CATEGORY'] = sample['ancestry_category']
                    table['COUNTRY OF RECRUITMENT'] = sample['country_recruitment']
                    table['ADDITIONAL ANCESTRY DESCRIPTION'] = sample['ancestry']
                    table['ANCESTRY DESCRIPTOR'] = sample['ancestry']
                    table['FOUNDER/GENETICALLY ISOLATED POPULATION'] = sample['ancestry_description']
                    table['NUMBER OF CASES'] = sample['cases']
                    table['NUMBER OF CONTROLS'] = sample['controls']
                    table['SAMPLE DESCRIPTION'] = sample['sample_description']
                    writer.writerow(table)

def build_ancestry_download_new(url, outputdir):
    #STUDY ACCESSION	FIRST AUTHOR	STAGE	NUMBER OF INDIVDUALS	BROAD ANCESTRAL CATEGORY	COUNTRY OF RECRUITMENT	ADDITONAL ANCESTRY DESCRIPTION	Founder/Genetically isolated population	Number of cases	Number of controls	Sample description	DOI
    with urllib.request.urlopen(url) as f:
        data = json.load(f)
        print(data)

        with open(outputdir + '/gwas-catalog-unpublished-ancestries-v1.0.3.1.tmp.tsv', 'w', newline='') as csvfile:
            fieldnames = ['STUDY ACCESSION', 'PUBMED ID', 'FIRST AUTHOR', 'DATE', 'INITIAL SAMPLE DESCRIPTION',
                          'REPLICATION SAMPLE DESCRIPTION', 'STAGE', 'NUMBER OF INDIVIDUALS',
                          'BROAD ANCESTRAL CATEGORY', 'COUNTRY OF ORIGIN', 'COUNTRY OF RECRUITMENT',
                          'ADDITIONAL ANCESTRY DESCRIPTION', 'ANCESTRY DESCRIPTOR',
                          'FOUNDER/GENETICALLY ISOLATED POPULATION',
                          'NUMBER OF CASES', 'NUMBER OF CONTROLS', 'SAMPLE DESCRIPTION']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)
            writer.writeheader()
            for study in data:
                table = defaultdict()
                table['STUDY ACCESSION'] = study['study_accession']
                table['PUBMED ID'] = 'NA'
                if not study['body_of_work']:
                    table['FIRST AUTHOR'] = ''
                else:
                    if 'first_author' in study['body_of_work'][0]:
                        table['FIRST AUTHOR'] = study['body_of_work'][0]['first_author']
                    else:
                        table['FIRST AUTHOR'] = 'NA'
                table['DATE'] = 'not yet curated'
                table['INITIAL SAMPLE DESCRIPTION'] = 'not yet curated'
                table['REPLICATION SAMPLE DESCRIPTION'] = 'not yet curated'
                for sample in study['unpublishedAncestries']:
                    table['STAGE'] = sample['stage']
                    table['NUMBER OF INDIVIDUALS'] = sample['sample_size']
                    table['BROAD ANCESTRAL CATEGORY'] = sample['ancestry_category']
                    table['COUNTRY OF RECRUITMENT'] = sample['country_recruitment']
                    table['ADDITIONAL ANCESTRY DESCRIPTION'] = sample['ancestry']
                    table['ANCESTRY DESCRIPTOR'] = sample['ancestry']
                    table['FOUNDER/GENETICALLY ISOLATED POPULATION'] = sample['ancestry_description']
                    table['NUMBER OF CASES'] = sample['cases']
                    table['NUMBER OF CONTROLS'] = sample['controls']
                    table['SAMPLE DESCRIPTION'] = sample['sample_description']
                    writer.writerow(table)


def build_studies_download(url, outputdir):
    with urllib.request.urlopen(url) as f:
        data = json.load(f)
        print(data)
        with open(outputdir + '/gwas-catalog-unpublished-studies-v1.0.3.tmp.tsv', 'w', newline='') as csvfile:
            fieldnames = ['DATE ADDED TO CATALOG', 'PUBMED ID', 'FIRST AUTHOR', 'DATE', 'JOURNAL', 'LINK', 'STUDY',
                          'DISEASE/TRAIT', 'INITIAL SAMPLE SIZE', 'REPLICATION SAMPLE SIZE',
                          'PLATFORM [SNPS PASSING QC]', 'ASSOCIATION COUNT', 'MAPPED TRAIT', 'MAPPED TRAIT URI',
                          'STUDY ACCESSION', 'GENOTYPING TECHNOLOGY', 'SUMMARY STATS LOCATION', 'SUBMISSION DATE',
                          'STATISTICAL MODEL', 'BACKGROUND TRAIT', 'MAPPED BACKGROUND TRAIT',
                          'MAPPED BACKGROUND TRAIT URI']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)

            writer.writeheader()
            for study in data:
                table = defaultdict()
                table['DATE ADDED TO CATALOG'] = 'not yet curated'
                table['STATISTICAL MODEL'] = study['statistical_model']
                table['DISEASE/TRAIT'] = study['trait']
                table['INITIAL SAMPLE SIZE'] = 'not yet curated'
                table['REPLICATION SAMPLE SIZE'] = 'not yet curated'
                table['PLATFORM [SNPS PASSING QC]'] = (study['array_manufacturer'] or 'NR') + ' [' + str(study['variant_count'] or 'NR') + ']'
                table['ASSOCIATION COUNT'] = 'not yet curated'
                table['MAPPED TRAIT'] = 'not yet curated'
                table['MAPPED TRAIT URI'] = 'not yet curated'
                table['STUDY ACCESSION'] = study['study_accession']
                table['GENOTYPING TECHNOLOGY'] = study['genotyping_technology']
                table['SUMMARY STATS LOCATION'] = generate_sumstats_ftp_path(study['study_accession'])
                table['SUBMISSION DATE'] = datetime.date.fromtimestamp(study['createdDate'] / 1000).isoformat()
                table['STATISTICAL MODEL'] = study['statistical_model']
                table['BACKGROUND TRAIT'] = study['background_trait']
                table['MAPPED BACKGROUND TRAIT'] = 'not yet curated'
                table['MAPPED BACKGROUND TRAIT URI'] = 'not yet curated'
                for bodyOfWork in study['body_of_work']:
                    table['STUDY'] = bodyOfWork['title']
                    table['PUBMED ID'] = 'not yet curated'
                    table['FIRST AUTHOR'] = bodyOfWork['first_author']
                    table['DATE'] = 'not yet curated'
                    table['JOURNAL'] = 'not yet curated'
                    table['LINK'] = bodyOfWork['doi']
                    writer.writerow(table)

def build_studies_download_new(url, outputdir):
    with urllib.request.urlopen(url) as f:
        data = json.load(f)
        print(data)
        with open(outputdir + '/gwas-catalog-unpublished-studies-v1.0.3.1.tmp.tsv', 'w', newline='') as csvfile:
            fieldnames = ['DATE ADDED TO CATALOG', 'PUBMED ID', 'FIRST AUTHOR', 'DATE', 'JOURNAL', 'LINK', 'STUDY',
                          'DISEASE/TRAIT', 'INITIAL SAMPLE SIZE', 'REPLICATION SAMPLE SIZE',
                          'PLATFORM [SNPS PASSING QC]', 'ASSOCIATION COUNT', 'MAPPED TRAIT', 'MAPPED TRAIT URI',
                          'STUDY ACCESSION', 'GENOTYPING TECHNOLOGY', 'SUBMISSION DATE',
                          'STATISTICAL MODEL', 'BACKGROUND TRAIT', 'MAPPED BACKGROUND TRAIT','MAPPED BACKGROUND TRAIT URI',
                          'COHORT', 'FULL SUMMARY STATISTICS', 'SUMMARY STATS LOCATION']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)

            writer.writeheader()
            for study in data:
                table = defaultdict()
                table['DATE ADDED TO CATALOG'] = 'not yet curated'
                table['STATISTICAL MODEL'] = study['statistical_model']
                table['DISEASE/TRAIT'] = study['trait']
                table['INITIAL SAMPLE SIZE'] = 'not yet curated'
                table['REPLICATION SAMPLE SIZE'] = 'not yet curated'
                table['PLATFORM [SNPS PASSING QC]'] = (study['array_manufacturer'] or 'NR') + ' [' + str(study['variant_count'] or 'NR') + ']'
                table['ASSOCIATION COUNT'] = 'not yet curated'
                table['MAPPED TRAIT'] = 'not yet curated'
                table['MAPPED TRAIT URI'] = 'not yet curated'
                table['STUDY ACCESSION'] = study['study_accession']
                table['GENOTYPING TECHNOLOGY'] = study['genotyping_technology']
                table['SUBMISSION DATE'] = datetime.date.fromtimestamp(study['createdDate'] / 1000).isoformat()
                table['STATISTICAL MODEL'] = study['statistical_model']
                table['BACKGROUND TRAIT'] = study['background_trait']
                table['MAPPED BACKGROUND TRAIT'] = 'not yet curated'
                table['MAPPED BACKGROUND TRAIT URI'] = 'not yet curated'
                table['COHORT'] = study['cohort']
                table['FULL SUMMARY STATISTICS'] = study['fullPvalueSet']
                table['SUMMARY STATS LOCATION'] = generate_sumstats_ftp_path(study['study_accession'])

                for bodyOfWork in study['body_of_work']:
                    table['STUDY'] = bodyOfWork['title']
                    table['PUBMED ID'] = 'not yet curated'
                    table['FIRST AUTHOR'] = bodyOfWork['first_author']
                    table['DATE'] = 'not yet curated'
                    table['JOURNAL'] = 'not yet curated'
                    table['LINK'] = bodyOfWork['doi']
                    writer.writerow(table)

def get_gcst_range(gcst):
    number_part = int(gcst.split("GCST")[1])
    floor = int(np.fix((number_part - 1) / RANGE_SIZE) * RANGE_SIZE) + 1
    upper = floor + (RANGE_SIZE -1)
    range_str = "GCST{f}-GCST{u}".format(f=str(floor).zfill(6), u=str(upper).zfill(6))
    return range_str

def generate_sumstats_ftp_path(gcst):
    range_bin = get_gcst_range(gcst)
    path = os.path.join(SUMSTAST_FTP_BASE_PATH, range_bin, gcst)
    return path

def main():
    base_url = 'http://localhost:8080'
    outputdir = "."
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:o:", ["url=", "output_dir="])
    except getopt.GetoptError:
        print('unpublished_study_export.py -u <base url> -o <output dir>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('unpublished_study_export.py -u <base url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            base_url = arg
        elif opt in ("-o", "--output_dir"):
            outputdir = arg
    url = base_url + '/gwas/rest/api/studies/unpublished'#replace w/ env. variable

    build_studies_download(url, outputdir)
    build_ancestry_download(url, outputdir)


if __name__ == '__main__':
    main()
