import pandas as pd
from gwas_data_sources import get_db_properties
import DBConnection
import argparse

class userManager(object):

    # list of sql queries:
    addToSecureUserSQL = '''
        INSERT INTO SECURE_USER(EMAIL, PASSWORD_HASH, ROLE_ID)
        VALUES(:email,
               :hash,
               :roleId)
        '''

    addToCuratorSQL = '''
        INSERT INTO CURATOR(EMAIL,FIRST_NAME,LAST_NAME)
        VALUES (:email, 
                :firstName,
                :lastName)
        '''

    addEventTypeSQL = '''
        INSERT INTO EVENT_TYPE(ID,ACTION,EVENT_TYPE, TRANSLATED_EVENT)
        VALUES ( EVENT_TYPE_SEQ.nextval,
                :action,
                :eventType,
                :event)
        '''

    checkUserSQL = '''
        SELECT SU.EMAIL, SU.PASSWORD_HASH, C.FIRST_NAME, C.LAST_NAME, C.FIRST_NAME, EVENT_TYPE
        FROM SECURE_USER SU,
            CURATOR C,
            EVENT_TYPE ET
        WHERE
          SU.EMAIL = :email
          AND SU.EMAIL = C.EMAIL
          AND C.LAST_NAME = ET.ACTION
        '''

    inactivateUserSQL = '''
        UPDATE SECURE_USER SU2
        SET SU2.PASSWORD_HASH = (
          SELECT SU1.PASSWORD_HASH
          FROM SECURE_USER SU1
          WHERE SU1.EMAIL = :adminEmail
        )
        WHERE SU2.EMAIL = :userEmail
        '''
    # initialize object by adding the connection object:
    def __init__(self, dbInstanceName):

        # Opening connection to database
        connectionObject = DBConnection.gwasCatalogDbConnector(dbInstanceName)
        self.__connection__ = connectionObject.connection
        self.__cursor__ = self.__connection__.cursor()

    def addUser(self, userinput):
        # Check if user exists:
        if self.__checkUser(userinput['emailAddress']):
            print('[Error] User with %s email is already exists in the database. Exiting.' % userinput['emailAddress'])
            exit()

        # Adding user to secure user table:
        self.__cursor__.execute(self.addToSecureUserSQL, {'email': userinput['emailAddress'], 
                                                 'hash' : userinput['passwordHash'], 
                                                 'roleId' : userinput['roleid']})

        # Adding user to curator table:
        self.__cursor__.execute(self.addToCuratorSQL, {'email': userinput['emailAddress'], 
                                              'firstName' : userinput['firstName'], 
                                              'lastName' : userinput['lastName']})

        # Adding user to event type table:
        self.__cursor__.execute(self.addEventTypeSQL, {'action': userinput['lastName'], 
                                              'event' : 'Study curator set to ' + userinput['lastName'], 
                                              'eventType' : 'STUDY_CURATOR_ASSIGNMENT_' + userinput['lastName'].upper()})

        # Check if user exists:
        if self.__checkUser(userinput['emailAddress']):
            print('[Info] User with %s email successfully added to the database.' % userinput['emailAddress'])
            self.__commit()
        else:
            print('[Warning] User was not added properly.')

    def inactivateUser(self, userinput):
        # Testing user email 1:
        if not self.__checkUser(userinput['userEmail']):
            print('[Error] User with %s email does not exist in the database. Exiting.' % userinput['userEmail'])
            exit()

        # Testing user email 2:
        if not self.__checkUser(userinput['adminEmail']):
            print('[Error] Administrator with %s email does not exist in the database. Exiting.' % userinput['adminEmail'])
            exit()
            
        # Updating hash:
        self.__cursor__.execute(self.inactivateUserSQL, {'userEmail': userinput['userEmail'], 
                                                 'adminEmail' : userinput['adminEmail']})
        self.__commit()

    def __commit(self):
        self.__connection__.commit()

    def __checkUser(self, userEmail):
        df = pd.read_sql(self.checkUserSQL, self.__connection__, params = {'email': userEmail})
        return(len(df))

def validateInput(userinput):

    # Checking if all values are specified:
    for key, value in userinput.items():
        if not value:
            print("[Error] %s is not specified. All fields are mandatory. Exiting." % key)
            exit()

    # Checking email:
    emailPattern = r'[^@]+@[^@]+\.[^@]+'
    if not re.match(emailPattern, userinput['emailAddress']):
        print('[Error] The provided email address is wrong: %s. Exiting.' % userinput['emailAddress'])
        exit()

##
## Action definitions:
## 
def createUser(dbManager):
    print("[Info] Creating new user in the curation interface of the GWAS Catalog")
    print("[Info] The following information is required for creating a new curator:")

    # Asking for the parameters:
    userinput = {}
    userinput['firstName'] = raw_input("Specify first name: ")
    userinput['lastName'] = raw_input("Specify last name: ")
    userinput['emailAddress'] = raw_input("Specify email address: ")
    userinput['role'] = raw_input("Specify role (admin/curator): ")
    userinput['passwordHash'] = raw_input("Specify password hash: ")

    # Adding role ID:
    userinput['roleid'] = '10057973' if userinput['role'] == 'curator' else '10057972'

    # Adding user:
    dbManager.addUser(userinput)

def modifyUser(dbManager):
    print("[Warning] User modification is not yet implemented.")

def inactivateUser(dbManager):
    print("[Info] Inactivating a user of the curation interface.")
    print("[Info] The following information is required to make the modification:")

    # Asking for the parameters:
    userinput = {}
    userinput['userEmail'] = raw_input("Specify e-mail of the user to be inactivated: ")
    userinput['adminEmail'] = raw_input("Specify e-mail of a admin user: ")

    # Adding user:
    dbManager.inactivateUser(userinput)

if __name__ == '__main__':

    # Parsing command line arguments:
    parser = argparse.ArgumentParser(description='This script was writen to manage users of the curation interface.')
    parser.add_argument('--dbInstanceName', default='dev2', type = str, choices=['spotpro','dev2','dev3'], help='Name of the database where the curator will be created.')
    parser.add_argument('--action', type = str, choices=['create', 'modify', 'inactivate'], help = 'Defining the type of action on the users.')

    args = parser.parse_args()
    action = args.action
    dbInstanceName = args.dbInstanceName

    print("[Info] Database instance name: %s" % dbInstanceName)

    dispatcher = {
        'create' : createUser,
        'modify' : modifyUser,
        'inactivate' : inactivateUser
    }
    
    # Initialize db connection:
    dbManager = userManager(dbInstanceName)

    # Dispatch db action:
    dispatcher[action](dbManager)



