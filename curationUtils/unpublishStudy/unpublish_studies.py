import argparse
from gwas_db_connect import DBConnection


class unpublishStudies:

    __unpublished__ = '''
        update housekeeping set catalog_unpublish_date = sysdate, last_update_date = sysdate, 
        unpublish_reason_id = 1 , is_published = 0, curation_status_id = 65
        where id in (select id  from housekeeping where id in (select housekeeping_id from 
        study where publication_id in ( select id from publication where pubmed_id = :pmid) and curation_status_id 
        not in (select id from curation_status where status = 'Requires Review')))
    '''


    __published__ =  '''
        update housekeeping set catalog_publish_date = sysdate, last_update_date = sysdate,  is_published = 1, 
        curation_status_id = 6, curator_id = 22 where id in (select id  from housekeeping where id in 
        (select housekeeping_id from study where publication_id in ( select id from publication where pubmed_id = :pmid) 
        and curation_status_id not in (select id from curation_status where status = 'Requires Review')))
    '''


    def __init__(self, dbInstanceName):

        # Opening connection to database
        self.__connection__ = DBConnection.gwasCatalogDbConnector(dbInstanceName)
        self.__cursor__ = self.__connection__.cursor

    def unpublishPmid(self, pmid):

        self.__cursor__.execute(self.__unpublished__, {'pmid': pmid})
        self.__connection__.connection.commit()
        self.__connection__.close()

    def publishPmid(self, pmid):

        self.__cursor__.execute(self.__published__, {'pmid': pmid})
        self.__connection__.connection.commit()
        self.__connection__.close()


def main():
    '''
    Create curation metrics.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser(description='This script was writen to unpublish studies for a Pmid.')
    parser.add_argument('--dbInstanceName', default='dev2', type = str, choices=['spotpro','dev2','dev3'], help='Name of the database where the curator will be created.')
    parser.add_argument('--pmid',type = str,help='Pmid for the unpublished studies')
    parser.add_argument('--action',type = str,choices=['pub','unpub'],help='Task to be performed')
    args = parser.parse_args()
    dbInstanceName = args.dbInstanceName
    pmid = args.pmid
    action = args.action
    dbhandler = unpublishStudies(dbInstanceName = dbInstanceName)
    if action == 'unpub':
        dbhandler.unpublishPmid(pmid)
    if action == 'pub':
        dbhandler.publishPmid(pmid)
    # Setting exit status:
    exitCode = 0
    quit(exitCode)


if __name__ == '__main__':
    main()
