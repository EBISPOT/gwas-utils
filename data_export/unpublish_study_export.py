import csv
import getopt
import json
import sys
import urllib.request
from collections import defaultdict


# def build_ancestry_download():
#     #STUDY ACCESSION	FIRST AUTHOR	STAGE	NUMBER OF INDIVDUALS	BROAD ANCESTRAL CATEGORY	COUNTRY OF RECRUITMENT	ADDITONAL ANCESTRY DESCRIPTION	Founder/Genetically isolated population	Number of cases	Number of controls	Sample description	DOI
#     url = 'http://localhost:8081/api/studies/unpublished'#replace w/ env. variable
#     with urllib.request.urlopen(url) as f:
#     #with open('C:/Users/jstewart/IdeaProjects/EBI/goci-new/goci-interfaces/goci-curation/src/main/resources/submissions.json', encoding='UTF-8') as f:
#         data = json.load(f)
#         print(data)
#
#         with open('unpublished_ancestry.tsv', 'w', newline='') as csvfile:
#             fieldnames = ['STUDY ACCESSION', 'FIRST AUTHOR', 'STAGE', 'NUMBER OF INDIVDUALS', 'BROAD ANCESTRAL CATEGORY', 'COUNTRY OF RECRUITMENT', 'ADDITONAL ANCESTRY DESCRIPTION', 'Founder/Genetically isolated population', 'Number of cases', 'Number of controls', 'Sample description', 'DOI']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)
#             writer.writeheader()
#             for study in data:
#                 table = defaultdict()
#                 table['STUDY ACCESSION'] = study['accession']
#                 table['FIRST AUTHOR'] = study['body_of_work'][0]['first_author']
#                 for sample in study['unpublishedAncestries']:
#                     table['NUMBER OF INDIVDUALS'] = sample['sample_size']
#                     table['STAGE'] = sample['stage']
#                     table['BROAD ANCESTRAL CATEGORY'] = sample['ancestry_category']
#                     table['COUNTRY OF RECRUITMENT'] = sample['country_recruitment']
#                     table['ADDITONAL ANCESTRY DESCRIPTION'] = sample['ancestry']
#                     table['Founder/Genetically isolated population'] = sample['ancestry_description']
#                     table['Number of cases'] = sample['cases']
#                     table['Number of controls'] = sample['controls']
#                     table['Sample description'] = sample['sample_description']
#                     table['DOI'] = study['body_of_work'][0]['doi']
#                     writer.writerow(table)


def build_studies_download(argv):
    base_url = 'http://localhost:8080'
    try:
        opts, args = getopt.getopt(argv, "hu:", ["url="])
    except getopt.GetoptError:
        print('unpublished_study_export.py -u <base url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('unpublished_study_export.py -u <base url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            base_url = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    url = base_url + '/gwas/rest/api/studies/unpublished'#replace w/ env. variable
    with urllib.request.urlopen(url) as f:
    #with open('C:/Users/jstewart/IdeaProjects/EBI/goci-new/goci-interfaces/goci-curation/src/main/resources/submissions.json', encoding='UTF-8') as f:
        data = json.load(f)
        print(data)
        with open('gwas-catalog-unpublished-studies-download.txt', 'w', newline='') as csvfile:
            fieldnames = ['STUDY ACCESSION', 'FIRST AUTHOR', 'STAGE', 'NUMBER OF INDIVDUALS', 'BROAD ANCESTRAL CATEGORY', 'COUNTRY OF RECRUITMENT', 'ADDITONAL ANCESTRY DESCRIPTION', 'Founder/Genetically isolated population', 'Number of cases', 'Number of controls', 'Sample description', 'DOI', 'DATE ADDED TO CATALOG', 'JOURNAL','STUDY', 'DISEASE/TRAIT', 'PLATFORM [SNPS PASSING QC]', 'GENOTYPING TECHNOLOGY', 'Statistical model']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.excel_tab)

            writer.writeheader()
            for study in data:
                table = defaultdict()
                table['STUDY ACCESSION'] = study['accession']
                table['DATE ADDED TO CATALOG'] = study['created_date']
                table['PLATFORM [SNPS PASSING QC]'] = study['array_manufacturer']
                table['GENOTYPING TECHNOLOGY'] = study['genotyping_technology']
                table['Statistical model'] = study['statistical_model']
                table['DISEASE/TRAIT'] = study['trait']
                for bodyOfWork in study['body_of_work']:
                    table['FIRST AUTHOR'] = bodyOfWork['first_author']
                    table['JOURNAL'] = bodyOfWork['journal']
                    #table['LINK'] = bodyOfWork['link']
                    table['STUDY'] = bodyOfWork['title']
                    table['DOI'] = bodyOfWork['doi']
                    for sample in study['unpublishedAncestries']:
                        table['NUMBER OF INDIVDUALS'] = sample['sample_size']
                        table['STAGE'] = sample['stage']
                        table['BROAD ANCESTRAL CATEGORY'] = sample['ancestry_category']
                        table['COUNTRY OF RECRUITMENT'] = sample['country_recruitment']
                        table['ADDITONAL ANCESTRY DESCRIPTION'] = sample['ancestry']
                        table['Founder/Genetically isolated population'] = sample['ancestry_description']
                        table['Number of cases'] = sample['cases']
                        table['Number of controls'] = sample['controls']
                        table['Sample description'] = sample['sample_description']
                    writer.writerow(table)


if __name__ == '__main__':
    build_studies_download(sys.argv[1:])

