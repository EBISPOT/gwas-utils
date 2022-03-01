import cx_Oracle
import argparse
from gwas_db_connect import DBConnection
import csv
import datetime


def get_curation_review_data(pmid, ancestry_mode, curator, database_name):
    '''
    Get data for Level 2 review.
    '''

    # List of queries
    curation_level2_data_sql = """
        SELECT S.ID, S.ACCESSION_ID, P.PUBMED_ID, A.FULLNAME,  
        TO_CHAR(P.PUBLICATION_DATE, 'dd-mm-yyyy'), P.PUBLICATION, P.TITLE, 
        TO_CHAR(H.STUDY_ADDED_DATE, 'dd-mm-yyyy'), CS.STATUS, TO_CHAR(H.CATALOG_PUBLISH_DATE, 'dd-mm-yyyy'), 
        S.INITIAL_SAMPLE_SIZE, S.REPLICATE_SAMPLE_SIZE
        FROM STUDY S, HOUSEKEEPING H, PUBLICATION P, AUTHOR A, CURATION_STATUS CS
        WHERE S.HOUSEKEEPING_ID=H.ID and S.PUBLICATION_ID=P.ID and P.FIRST_AUTHOR_ID=A.ID
            and H.CURATION_STATUS_ID=CS.ID
            and P.PUBMED_ID= :pmid
    """

    study_dup_tag_sql = """
        SELECT N.TEXT_NOTE
        FROM STUDY S, NOTE N
        WHERE S.ID=N.STUDY_ID
          and N.NOTE_SUBJECT_ID=9
          and S.ID= :study_id
    """

    study_platform_sql = """
        SELECT listagg(PLA.MANUFACTURER, ', ') WITHIN GROUP (ORDER BY PLA.MANUFACTURER), S.QUALIFIER, S.SNP_COUNT, S.IMPUTED 
        FROM PLATFORM PLA, STUDY_PLATFORM SP, STUDY S
        WHERE PLA.ID=SP.PLATFORM_ID and SP.STUDY_ID=S.ID
              and S.ID= :study_id
        GROUP BY S.QUALIFIER, S.SNP_COUNT, S.IMPUTED
    """

    study_genotyping_technology_sql = """
        SELECT listagg(GT.GENOTYPING_TECHNOLOGY) WITHIN GROUP (ORDER BY GT.GENOTYPING_TECHNOLOGY)
        FROM STUDY S, STUDY_GENOTYPING_TECHNOLOGY SGT, GENOTYPING_TECHNOLOGY GT
        WHERE S.ID=SGT.STUDY_ID and SGT.GENOTYPING_TECHNOLOGY_ID=GT.ID 
            and S.ID= :study_id
    """

    study_reported_trait_sql = """
        SELECT listagg(DT.TRAIT, ', ')  WITHIN GROUP (ORDER BY DT.TRAIT) 
        FROM STUDY S, STUDY_DISEASE_TRAIT SDT, DISEASE_TRAIT DT 
        WHERE S.ID=SDT.STUDY_ID and SDT.DISEASE_TRAIT_ID=DT.ID 
            and S.ID= :study_id
    """

    study_mapped_trait_sql = """
        SELECT listagg(ET.TRAIT, ', ')  WITHIN GROUP (ORDER BY ET.TRAIT), ET.URI
        FROM STUDY S, STUDY_EFO_TRAIT SETR, EFO_TRAIT ET
        WHERE S.ID=SETR.STUDY_ID and SETR.EFO_TRAIT_ID=ET.ID
          and S.ID= :study_id
        GROUP BY ET.URI
    """

    study_association_cnt_sql = """
        SELECT COUNT(A.ID)
        FROM STUDY S, ASSOCIATION A
        WHERE S.ID=A.STUDY_ID 
            and S.ID= :study_id
    """

    # Queries for Expanded Ancestry Option
    expanded_ancestry_sql = """
        SELECT A.ID, A.TYPE, A.NUMBER_OF_INDIVIDUALS, A.DESCRIPTION
        FROM STUDY S, ANCESTRY A
        WHERE A.STUDY_ID=S.ID
          and S.ID= :study_id 
    """

    ancestral_group_sql = """
        SELECT listagg(AG.ANCESTRAL_GROUP, ', ') WITHIN GROUP (ORDER BY AG.ANCESTRAL_GROUP) 
        FROM ANCESTRY A, ANCESTRY_ANCESTRAL_GROUP AAG, ANCESTRAL_GROUP AG 
        WHERE A.ID=AAG.ANCESTRY_ID and AAG.ANCESTRAL_GROUP_ID=AG.ID 
            and A.ID= :ancestry_id
    """

    ancestry_country_of_origin_sql = """
        SELECT listagg(C.COUNTRY_NAME, ', ') WITHIN GROUP (ORDER BY C.COUNTRY_NAME)
        FROM ANCESTRY A, ANCESTRY_COUNTRY_OF_ORIGIN ACOO, COUNTRY C 
        WHERE A.ID=ACOO.ANCESTRY_ID and ACOO.COUNTRY_ID=C.ID 
            and A.ID= :ancestry_id
    """

    ancestry_country_of_recruitment = """
        SELECT listagg(C.COUNTRY_NAME, ', ') WITHIN GROUP (ORDER BY C.COUNTRY_NAME) 
        FROM ANCESTRY A, ANCESTRY_COUNTRY_RECRUITMENT ACOR, COUNTRY C 
        WHERE A.ID=ACOR.ANCESTRY_ID and ACOR.COUNTRY_ID=C.ID 
            and A.ID= :ancestry_id
    """

    all_level2_data = []

    if ancestry_mode == 'collapsed':
        level2_attr_list = ['STUDY_ID', 'DUP_TAG', 'REPORTED_TRAIT', 'STUDY_CREATION_DATE', 'CURATION_STATUS',
                            'STUDY_ACCCESSION', \
                            'CATALOG_PUBLISH_DATE', 'PUBMED_ID', 'FIRST_AUTHOR', 'PUBLICATION_DATE', 'JOURNAL', 'LINK',
                            'TITLE', 'PLATFORM [SNPS PASSING QC]', \
                            'ASSOCIATION_COUNT', 'MAPPED_TRAIT', 'MAPPED_TRAIT_URI', 'GENOTYPING_TECHNOLOGY',
                            'INITIAL_SAMPLE_DESCRIPTION', \
                            'REPLICATION_SAMPLE_DESCRIPTION']
    else:
        level2_attr_list = ['STUDY_ID', 'DUP_TAG', 'REPORTED_TRAIT', 'STUDY_CREATION_DATE', 'CURATION_STATUS',
                            'STUDY_ACCCESSION', \
                            'CATALOG_PUBLISH_DATE', 'PUBMED_ID', 'FIRST_AUTHOR', 'PUBLICATION_DATE', 'JOURNAL', 'LINK',
                            'TITLE', 'PLATFORM [SNPS PASSING QC]', \
                            'ASSOCIATION_COUNT', 'MAPPED_TRAIT', 'MAPPED_TRAIT_URI', 'GENOTYPING_TECHNOLOGY',
                            'INITIAL_SAMPLE_DESCRIPTION', \
                            'REPLICATION_SAMPLE_DESCRIPTION', 'STAGE', 'NUMBER_OF_INDIVIDUALS',
                            'BROAD_ANCESTRAL_CATEGORY', 'COUNTRY_OF_ORIGIN', \
                            'COUNTRY_OF_RECRUITMENT', 'ADDITONAL_ANCESTRY_DESCRIPTION']

    # Get First Author name to include in output filename
    first_author_sql = """
        SELECT REPLACE(A.FULLNAME_STANDARD, ' ', '')
        FROM PUBLICATION P, AUTHOR A 
        WHERE P.FIRST_AUTHOR_ID=A.ID 
            and P.PUBMED_ID= :pmid
    """

    first_author = ""
    try:
        db_handler = DBConnection.gwasCatalogDbConnector(database_name)
        cursor = db_handler.cursor
        cursor.prepare(first_author_sql)
        cursor.execute(None, {'pmid': pmid})
        first_author_data = cursor.fetchone()
        first_author = first_author_data[0]

    except cx_Oracle.DatabaseError as exception:
        print(exception)

    TIMESTAMP = get_timestamp()

    outfile = open(first_author + "_" + pmid + "-" + ancestry_mode + "_" + curator + "_" + TIMESTAMP + ".csv", "w")
    csvout = csv.writer(outfile)
    csvout.writerow(level2_attr_list)

    # Get data for curation review file
    try:
        db_handler = DBConnection.gwasCatalogDbConnector(database_name)
        cursor = db_handler.cursor
        cursor.prepare(curation_level2_data_sql)
        cursor.execute(None, {'pmid': pmid})
        curation_queue_data = cursor.fetchall()

        for data in curation_queue_data:

            data_results = {}

            data_results['STUDY_ID'] = data[0]

            # Account for studies that do not yet have an AccessionId
            if data[1] is None:
                data_results['STUDY_ACCCESSION'] = 'Not yet assigned'
            else:
                data_results['STUDY_ACCCESSION'] = data[1]

            data_results['PUBMED_ID'] = data[2]
            data_results['LINK'] = 'https://www.ncbi.nlm.nih.gov/pubmed/' + data[2]

            data_results['FIRST_AUTHOR'] = data[3]

            data_results['PUBLICATION_DATE'] = data[4]

            data_results['JOURNAL'] = data[5]

            data_results['TITLE'] = data[6]

            data_results['STUDY_CREATION_DATE'] = data[7]

            data_results['CURATION_STATUS'] = data[8]

            if data[9] is None:
                data_results['CATALOG_PUBLISH_DATE'] = 'None'
            else:
                data_results['CATALOG_PUBLISH_DATE'] = data[9]

            if data[10] is None:
                data_results['INITIAL_SAMPLE_DESCRIPTION'] = 'None'
            else:
                data_results['INITIAL_SAMPLE_DESCRIPTION'] = data[10]

            if data[11] is None:
                data_results['REPLICATION_SAMPLE_DESCRIPTION'] = 'None'
            else:
                data_results['REPLICATION_SAMPLE_DESCRIPTION'] = data[11]

            #############################
            # Get Study Dup Tag
            #############################
            cursor.prepare(study_dup_tag_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            dup_tag = cursor.fetchone()

            if not dup_tag:
                data_results['DUP_TAG'] = 'None'
            else:
                data_results['DUP_TAG'] = dup_tag[0]

            ##############################
            # Get Platform and Qualifier
            ##############################
            cursor.prepare(study_platform_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            platform = cursor.fetchall()

            if not platform:
                data_results['PLATFORM [SNPS PASSING QC]'] = 'None'
            else:
                qualifier = platform[0][1] if platform[0][1] != None else ''
                imputed = 'imputed' if platform[0][3] == 1 else ''

                platform_snps_qc = platform[0][0] + " [" + qualifier + str(platform[0][2]) + "] (" + imputed + ")"
                data_results['PLATFORM [SNPS PASSING QC]'] = platform_snps_qc

            #############################
            # Get Genotyping Technology
            #############################
            cursor.prepare(study_genotyping_technology_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            genotyping_technology = cursor.fetchone()

            if not genotyping_technology:
                data_results['GENOTYPING_TECHNOLOGY'] = 'None'
            else:
                data_results['GENOTYPING_TECHNOLOGY'] = genotyping_technology[0]

            ##########################
            # Get Reported Trait
            ##########################
            cursor.prepare(study_reported_trait_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            reported_trait = cursor.fetchone()

            if not reported_trait:
                data_results['REPORTED_TRAIT'] = 'None'
            else:
                data_results['REPORTED_TRAIT'] = reported_trait[0]

            ##########################
            # Get Mapped/EFO Trait
            ##########################
            cursor.prepare(study_mapped_trait_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            mapped_trait = cursor.fetchone()

            if not mapped_trait:
                data_results['MAPPED_TRAIT'] = 'None'
                data_results['MAPPED_TRAIT_URI'] = 'None'
            else:
                data_results['MAPPED_TRAIT'] = mapped_trait[0]
                data_results['MAPPED_TRAIT_URI'] = mapped_trait[1]

            ##########################
            # Get Association count
            ##########################
            cursor.prepare(study_association_cnt_sql)
            r = cursor.execute(None, {'study_id': data[0]})
            association_cnt = cursor.fetchone()

            data_results['ASSOCIATION_COUNT'] = association_cnt[0]

            #######################
            # Expanded Ancestry
            #######################
            if ancestry_mode == 'expanded':

                # General Ancestry information
                cursor.prepare(expanded_ancestry_sql)
                r = cursor.execute(None, {'study_id': data[0]})
                general_ancestry = cursor.fetchall()

                for ancestry in general_ancestry:
                    expanded_ancestry = {}

                    expanded_ancestry['STAGE'] = ancestry[1]
                    expanded_ancestry['NUMBER_OF_INDIVIDUALS'] = ancestry[2]
                    expanded_ancestry['ADDITONAL_ANCESTRY_DESCRIPTION'] = ancestry[3]

                    ancestry_id = ancestry[0]

                    cursor.prepare(ancestral_group_sql)
                    r = cursor.execute(None, {'ancestry_id': ancestry_id})
                    ancestral_group = cursor.fetchone()
                    expanded_ancestry['BROAD_ANCESTRAL_CATEGORY'] = ancestral_group[0]

                    cursor.prepare(ancestry_country_of_origin_sql)
                    r = cursor.execute(None, {'ancestry_id': ancestry_id})
                    ancestral_coo = cursor.fetchone()
                    expanded_ancestry['COUNTRY_OF_ORIGIN'] = ancestral_coo[0]

                    cursor.prepare(ancestry_country_of_recruitment)
                    r = cursor.execute(None, {'ancestry_id': ancestry_id})
                    ancestral_cor = cursor.fetchone()
                    expanded_ancestry['COUNTRY_OF_RECRUITMENT'] = ancestral_cor[0]

                    # Update data_results dict
                    data_results.update(expanded_ancestry)

                    # Write out results
                    data_keys = data_results.keys()
                    results = [(data_results[key]) for key in level2_attr_list if key in data_keys]
                    csvout.writerow(results)


            else:
                # Write out results
                data_keys = data_results.keys()
                results = [(data_results[key]) for key in level2_attr_list if key in data_keys]
                csvout.writerow(results)

    except cx_Oracle.DatabaseError as exception:
        print(exception)


def get_timestamp():
    '''
    Get timestamp of current date and time.
    '''
    timestamp = '{:%Y-%m-%d-%H-%M}'.format(datetime.datetime.now())
    return timestamp

def main():
    '''
    Create Level2 curation check file.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', default='SPOTPRO', choices=['SPOTPRO'],
                        help='Run as (default: SPOTPRO).')
    parser.add_argument('--pmid', default='28256260', help='Add Pubmed Identifier, e.g. 28256260.')
    parser.add_argument('--ancestry', default='collapsed', choices=['collapsed', 'expanded'],
                        help='Run as (default: collapsed).')
    parser.add_argument('--username', default='gwas-curator', help='Run as (default: gwas-curator).')
    args = parser.parse_args()

    database_name = args.database
    pmid = args.pmid
    ancestry = args.ancestry
    username = args.username

    get_curation_review_data(pmid, ancestry, username, database_name)


if __name__ == '__main__':
    main()



