import pandas as pd
from gwas_db_connect import DBConnection

class getDataFromDB(object):

    __assocSQL__ = '''
        SELECT A.ID, A.STUDY_ID, S.ACCESSION_ID
        FROM ASSOCIATION A,
            STUDY S
        WHERE S.ID = A.STUDY_ID
    '''

    __studySQL__ = '''
        SELECT S.ACCESSION_ID, S.ID, P.PUBMED_ID, P.TITLE, HK.LAST_UPDATE_DATE, HK.CATALOG_PUBLISH_DATE, HK.CATALOG_UNPUBLISH_DATE
        FROM STUDY S,
            PUBLICATION P,
            HOUSEKEEPING HK
        WHERE S.HOUSEKEEPING_ID = HK.ID
        AND S.PUBLICATION_ID = P.ID
        AND HK.IS_PUBLISHED = 1
    '''

    __unpublished__ = '''
        SELECT S.ACCESSION_ID, S.ID, P.PUBMED_ID, P.TITLE, HK.LAST_UPDATE_DATE, HK.CATALOG_PUBLISH_DATE, HK.CATALOG_UNPUBLISH_DATE
        FROM STUDY S,
            PUBLICATION P,
            HOUSEKEEPING HK
        WHERE S.HOUSEKEEPING_ID = HK.ID
        AND S.PUBLICATION_ID = P.ID
        AND HK.IS_PUBLISHED = 0
    '''
    
    # Init
    def __init__(self, instance):
        connection = DBConnection.gwasCatalogDbConnector(instance)
        
        print("[INFO] Extracting data from %s" % instance)
        self.__getAssocData__(connection.connection)
        self.__getStudyData__(connection.connection)
        self.__getUnpublished__(connection.connection)
        
        # Closing connection: 
        print("[INFO] Closing connection.")
        connection.close()
    
    # Get assoc Data
    def __getAssocData__(self, connection):
        self.__assocData__ = pd.read_sql(self.__assocSQL__, connection)
        
    # Get study data
    def __getStudyData__(self, connection):
        self.__studyData__ = pd.read_sql(self.__studySQL__, connection)
    
    # Get unpublished data:
    def __getUnpublished__(self, connection):
        self.__unpublished__ =  pd.read_sql(self.__unpublished__, connection)

    # Returnd study count:
    def getStudyCount(self):
        return(len(self.__studyData__))
    
    # Return study df:
    def getStudy(self):
        return(self.__studyData__)
    
    # Return assoc count
    def getAssocCount(self):
        return(len(self.__assocData__))    
    
    # Return assoc df:
    def getAssoc(self):
        return(self.__assocData__)
    
    # Return unpublished data:
    def getUnpublished(self):
        return(self.__unpublished__)


