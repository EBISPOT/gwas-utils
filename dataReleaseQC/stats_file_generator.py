import re
import requests
from datetime import datetime
import argparse

from gwas_db_connect import DBConnection

"""
This script generates stats file as part of the data release process. The stats file then used by the UI application, so the format and content is
tightly defined. The content of the file should look like this:

#Tue Sep 24 10:33:21 BST 2019
dbsnpbuild=151
studycount=4220
associationcount=157336
genomebuild=GRCh38.p12
releasedate=2019-09-24
snpcount=107486
ensemblbuild=96
efoversion=v3.54.0
"""

def get_db_counts(connection):
    # studycount=4220
    # associationcount=157336
    # snpcount=107486
   
    '''
    Warning: It might be confusing, but studycount actually publicationcount in the final document.
    
    That's why in the code, I'm referring to that value as publication count. :D 
    '''

    returnData = {
        'studycount' : None,
        'associationcount' : None,
        'snpcount' : None
    }
     
    # Get study count:
    publicationCountSql = '''
        SELECT COUNT(DISTINCT(P.PUBMED_ID))
        FROM PUBLICATION P,
          STUDY S,
          HOUSEKEEPING HK
        WHERE HK.ID = S.HOUSEKEEPING_ID
          AND HK.IS_PUBLISHED = 1
          AND S.PUBLICATION_ID = P.ID
        ''' 
    connection.cursor.execute(publicationCountSql)
    returnData['studycount'] = connection.cursor.fetchall()[0][0]
    
    # Get association Count:
    associationCountSql = '''
        SELECT COUNT(DISTINCT(A.ID))
        FROM ASSOCIATION A,
          STUDY S,
          HOUSEKEEPING HK
        WHERE HK.ID = S.HOUSEKEEPING_ID
          AND HK.IS_PUBLISHED = 1
          AND A.STUDY_ID = S.ID
        '''
    connection.cursor.execute(associationCountSql)
    returnData['associationcount'] = connection.cursor.fetchall()[0][0]
    
    # Get snp count:
    snpCountSql = '''
        SELECT COUNT(DISTINCT(SNP.RS_ID))
        FROM ASSOCIATION A,
          SINGLE_NUCLEOTIDE_POLYMORPHISM SNP,
          STUDY S,
          HOUSEKEEPING HK,
          ASSOCIATION_SNP_VIEW ASV
        WHERE HK.ID = S.HOUSEKEEPING_ID
          AND HK.IS_PUBLISHED = 1
          AND A.STUDY_ID = S.ID
          AND A.ID = ASV.ASSOCIATION_ID
          AND SNP.ID = ASV.SNP_ID
        '''
    connection.cursor.execute(snpCountSql)
    returnData['snpcount'] = connection.cursor.fetchall()[0][0]
    
    publishedSsCountSql = '''
        SELECT COUNT(*)
        FROM STUDY S,
            PUBLICATION P,
            HOUSEKEEPING HK
        WHERE S.HOUSEKEEPING_ID = HK.ID
            AND S.PUBLICATION_ID = P.ID
            AND HK.IS_PUBLISHED = 1
            AND S.FULL_PVALUE_SET = 1
        '''
    connection.cursor.execute(publishedSsCountSql)
    publishedSsCount = connection.cursor.fetchall()[0][0]

    unpublishedSsCountSql = '''
        SELECT COUNT(*)
        FROM UNPUBLISHED_STUDY
        WHERE SUMMARY_STATS_FILE IS NOT NULL
        '''
    connection.cursor.execute(unpublishedSsCountSql)
    returnData['sscount'] = connection.cursor.fetchall()[0][0] + publishedSsCount
    
    return returnData


def get_ensembl_info(ensembl_url):
    
    # The following values are returned:
    returnData = {
        'genomebuild' : None,
        'ensemblbuild' : None,
        'dbsnpbuild' : None
    }
    
    # Is the rest API is up:
    is_server_up = ensembl_url + '/info/ping?content-type=application/json'
    
    try:
        r = requests.get(is_server_up)
        data = r.json()
        
        if data['ping'] == 1:
            print('[Info] Ensembl REST API is up and running.')
        else:
            print('[Info] Ensembl REST API is down.')
    except:
        print('[Warning] Failed to retrieve data from Ensembl\'s REST API.')
        return returnData
    
    # Get build version:
    get_assembly_name = ensembl_url + '/info/assembly/homo_sapiens?content-type=application/json'
    try:
        r = requests.get(get_assembly_name)
        data = r.json()
        returnData['genomebuild'] = data['assembly_name']
    except:
        print('[Warning] Failed to genome build version from Ensembl\'s REST API.')
    
    # Get data version:
    get_ensembl_version = ensembl_url + '/info/data/?content-type=application/json'
    try:
        r = requests.get(get_ensembl_version)
        data = r.json()
        returnData['ensemblbuild'] = data['releases'][0]
    except:
        print(get_ensembl_version)
        print('[Warning] Could not retrieve Ensembl version from Ensembl\'s REST API.')
    
    # Get dbsnp version:
    get_db_snp_version = ensembl_url + '/info/variation/homo_sapiens?content-type=application/json&filter=dbSNP'
    try:
        r = requests.get(get_db_snp_version)
        data = r.json()
        returnData['dbsnpbuild'] = data[0]['version']
    except:
        print(get_ensembl_version)
        print('[Warning] Could not retrieve dbSNP version from Ensembl\'s REST API.')    
    return returnData

def get_efo_info():
    try:
        version = requests.get('https://api.github.com/repos/EBISPOT/efo/releases/latest').json()['tag_name']
        returnData['efoversion'] = version
    except:
        print('[Warning] Failed to retrieve EFO version from Github API.')
    return returnData


def read_application_properties(fileName):
    """
    This function reads the provided application properties file.
    """

    properties = {}

    try:
        with open(fileName, 'r') as propfile:
            lines = (line.rstrip() for line in propfile) # All lines including the blank ones
            lines = (line for line in lines if line) # Non-blank lines
            
            for line in lines:
                
                # Skip line with hash:
                if line.startswith("#"):
                    continue
                
                if '=' in line:
                    line = line.replace("=", " ")
                else:
                    line = re.sub(" +"," ",line)
                properties[line.split(" ")[0]] = line.split(" ")[1]
    except:
        print(line)
        
    return properties

def main():
    # Commandline arguments
    parser = argparse.ArgumentParser(
        description='This script generates stats file as part of the data release process. The stats file then used by the UI application, so the format and content is tightly defined.')
    parser.add_argument('--propertiesFile', type=str, help='The production application properties file.')
    parser.add_argument('--outputFile', default='gwas-catalog-stats.txt',
                        help='Name of the stats file generated as output.')
    parser.add_argument('--dbInstance', help='Name of the database instance from which the counts are extracted.')

    args = parser.parse_args()

    # Input parameters:
    applicationProperties = args.propertiesFile
    StatsFilename = args.outputFile
    dbInstance = args.dbInstance

    # Read application properties:
    properties = read_application_properties(applicationProperties)

    # Extract ensembl URL from the properties:
    ensUrl = properties['ensembl.server']

    # Fetch data from Ensembl:
    statsData = get_ensembl_info(ensUrl)
    
    # Fetch EFO Version from GitHub
    statsData = get_efo_info();

    # Adding date of release:
    today = datetime.now()
    statsData['releasedate'] = today.strftime("%Y-%m-%d")

    # Extract data from database:
    # dbInstance = properties['spring.datasource.url'].split(':')[-1] # No longer read from the properties file!
    connection = DBConnection.gwasCatalogDbConnector(database_name=dbInstance)

    # Update dictionary with the counts:
    statsData.update(get_db_counts(connection))

    # Write file:
    with open(StatsFilename, 'w') as statsfile:
        # Write header:
        statsfile.write('# {:%c %z}\n'.format(datetime.now()))

        for key, value in statsData.items():
            statsfile.write('{}={}\n'.format(key, value))

    print('[Info] Stats file successfully generated.')


if __name__ == "__main__":
    main()

