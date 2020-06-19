import csv
import datetime
import getopt
import json
import sys
import urllib.request
from collections import defaultdict


def build_ancestry_download(url, outputdir):
    #STUDY ACCESSION	FIRST AUTHOR	STAGE	NUMBER OF INDIVDUALS	BROAD ANCESTRAL CATEGORY	COUNTRY OF RECRUITMENT	ADDITONAL ANCESTRY DESCRIPTION	Founder/Genetically isolated population	Number of cases	Number of controls	Sample description	DOI
    with urllib.request.urlopen(url) as f:
    #with open('C:/Users/jstewart/IdeaProjects/EBI/goci-new/goci-interfaces/goci-curation/src/main/resources/submissions.json', encoding='UTF-8') as f:
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
                table['FIRST AUTHOR'] = study['body_of_work'][0]['first_author']
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


def build_studies_download(url, outputdir):
    with urllib.request.urlopen(url) as f:
    #with open('C:/Users/jstewart/IdeaProjects/EBI/goci-new/goci-interfaces/goci-curation/src/main/resources/submissions.json', encoding='UTF-8') as f:
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
                table['PLATFORM [SNPS PASSING QC]'] = study['array_manufacturer']
                table['ASSOCIATION COUNT'] = 'not yet curated'
                table['MAPPED TRAIT'] = 'not yet curated'
                table['MAPPED TRAIT URI'] = 'not yet curated'
                table['STUDY ACCESSION'] = study['study_accession']
                table['GENOTYPING TECHNOLOGY'] = study['genotyping_technology']
                table['SUMMARY STATS LOCATION'] = 'ftp://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/' + study['study_accession']
                table['SUBMISSION DATE'] = datetime.date.fromtimestamp(study['createdDate'] / 1000).isoformat()
                table['STATISTICAL MODEL'] = study['statistical_model']
                table['BACKGROUND TRAIT'] = study['background_trait']
                table['MAPPED BACKGROUND TRAIT'] = 'not yet curated'
                table['MAPPED BACKGROUND TRAIT URI'] = 'not yet curated'
              #  table['STUDY'] = study['study_description']
                for bodyOfWork in study['body_of_work']:
                    table['PUBMED ID'] = 'not yet curated'
                    table['FIRST AUTHOR'] = bodyOfWork['first_author']
                    table['DATE'] = 'not yet curated'
                    table['JOURNAL'] = 'not yet curated'
                    table['LINK'] = bodyOfWork['doi']
                    writer.writerow(table)


if __name__ == '__main__':
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

