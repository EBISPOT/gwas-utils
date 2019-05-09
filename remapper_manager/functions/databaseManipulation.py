import pandas as pd
from gwas_data_sources import get_db_properties
import DBConnection


class databaseManipulation(object):

    # Query to return the list of IDs that will be remapped:
    __getIDsToRemap__ = '''SELECT *
            FROM (select ID
                FROM ASSOCIATION
                WHERE ID > :startID
                ORDER BY ID ASC)
            WHERE ROWNUM <= :rowsCnt
            ORDER BY ID DESC
        '''

    # Get unmapped IDs:
    __getUnmappedIDs__ = '''SELECT A.ID
            FROM ASSOCIATION A
            WHERE
                A.ID > :startID
                AND A.ID <= :endID
                AND A.LAST_MAPPING_DATE IS null
            ORDER BY A.ID ASC
        '''

    # Get the number of unmapped associations:
    __getUnmappedCounts__ = '''SELECT COUNT(ID) AS COUNT
            FROM ASSOCIATION A
            WHERE 
                A.LAST_MAPPING_DATE IS null
        '''

    # Remove last mapped date:
    __removeMapping__ = '''UPDATE ASSOCIATION A
            SET A.LAST_MAPPING_DATE = null, 
                A.LAST_MAPPING_PERFORMED_BY = NULL
            WHERE A.ID >= :startID 
                AND A.ID <= :endID
        '''

    # remove mapping from association report:
    __removeAssociationReport__ = '''DELETE FROM ASSOCIATION_REPORT AR
            WHERE AR.ASSOCIATION_ID >= :startID  
                AND AR.ASSOCIATION_ID <= :endID
        '''
    
    # Counting associations between two IDs:
    __countIds__ = '''SELECT COUNT(*) AS COUNT
            FROM ASSOCIATION A
            WHERE A.ID >= :startID
                AND A.ID <= :endID
        '''

    def __init__(self, dbName = 'dev2'):
        connectionObject = DBConnection.gwasCatalogDbConnector(dbName)
        self.__connection__ = connectionObject.connection

    def getFirstToRemap(self, start, end):
        unmappedDf = pd.read_sql(self.__getUnmappedIDs__, self.__connection__, params = {'startID': int(start), 'endID' : int(end)})
        
        print("[Info] Between %s and %s there are %s unmpped associations." %(start, end, len(unmappedDf)))

        if len(unmappedDf) == 0:
            firstUnmappedId = end
        else:
            firstUnmappedId = unmappedDf.ID.min()
        return(firstUnmappedId)

    def getLastToRemap(self, start, rows):
        IdList = pd.read_sql(self.__getIDsToRemap__, self.__connection__, params={'startID': int(start), 'rowsCnt': int(rows) })
        lastId = IdList.max().tolist()[0]
        return(lastId)

    def getUnmappedCount(self):
        unmapped_count = pd.read_sql(self.__getUnmappedCounts__, self.__connection__).COUNT.tolist()[0]
        return(unmapped_count)

    def removeMapping(self, startID, endID):
        
        # Deleting last update date
        cursor = self.__connection__.cursor()
        cursor.execute(self.__removeMapping__, {'startID': int(startID), 'endID' : int(endID)})
        self.__connection__.commit()
        cursor.close()
        
        # Deleting report
        cursor = self.__connection__.cursor()
        cursor.execute(self.__removeAssociationReport__, {'startID': int(startID), 'endID' : int(endID)})
        self.__connection__.commit()
        cursor.close()
        
    def getAssociationCount(self, startID, endID):
        countDf = pd.read_sql( self.__countIds__, self.__connection__, params={'startID': int(startID), 'endID': int(endID) })
        return(countDf.COUNT.tolist()[0])
    
    def closeConnection(self):
        self.__connection__.close()

