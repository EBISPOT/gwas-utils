import pandas as pd
import argparse

from gwas_db_connect import DBConnection

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
        SELECT SU.EMAIL, SU.PASSWORD_HASH, C.FIRST_NAME, C.LAST_NAME, EVENT_TYPE
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
    
    updateSecureUser = '''
        UPDATE SECURE_USER SU
        SET SU.EMAIL = :NEW_EMAIL, SU.PASSWORD_HASH = :PASSWORD_HASH
        WHERE SU.EMAIL = :OLD_EMAIL
        '''
    
    updateCurator = '''
        UPDATE CURATOR C
        SET C.EMAIL = :NEW_EMAIL, C.FIRST_NAME = :FIRST_NAME, C.LAST_NAME = :LAST_NAME
        WHERE C.EMAIL = :OLD_EMAIL
        '''
    
    updateEventType = '''
        UPDATE EVENT_TYPE ET
        SET ET.ACTION = :ACTION, ET.EVENT_TYPE = :EVENT_TYPE, ET.TRANSLATED_EVENT = :TRANSLATED_EVENT
        WHERE ET.ACTION = :OLD_LAST_NAME
        '''
    
    # initialize object by adding the connection object:
    def __init__(self, dbInstanceName):

        # Opening connection to database
        connectionObject = DBConnection.gwasCatalogDbConnector(dbInstanceName)
        self.__connection__ = connectionObject.connection
        self.__cursor__ = self.__connection__.cursor()

    def addUser(self, userinput):
        # Check if user exists:
        if self.checkUser(userinput['emailAddress']):
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
            
    def updateUserInfo(self, oldEmail, userinput):

        # fetch old dataframe with all the data:
        if self.checkUser(oldEmail):
            current_user_df = self.actual_user_data
        else:
            return 1
        
        # If the email or the password hash is given, we have to update the secure user table:
        if ('EMAIL' in userinput) or ('PASSWORD_HASH' in userinput):
            sendData = {'OLD_EMAIL' : oldEmail}
            sendData['NEW_EMAIL'] = userinput['EMAIL'] if 'EMAIL' in userinput else oldEmail
            sendData['PASSWORD_HASH'] = userinput['PASSWORD_HASH'] if 'PASSWORD_HASH' in userinput else current_user_df.PASSWORD_HASH.tolist()[0]
            
            # Update secure user table with data:
            self.__cursor__.execute(self.updateSecureUser, sendData)
            print('[Info] Changes to SECURE_USER table has been submitted.')
            
        # If email, first name or last name is changed, update curator table:
        if ('EMAIL' in userinput) or ('FIRST_NAME' in userinput) or ('LAST_NAME' in userinput):
            sendData = {'OLD_EMAIL' : oldEmail}
            sendData['NEW_EMAIL'] = userinput['EMAIL'] if 'EMAIL' in userinput else oldEmail
            sendData['FIRST_NAME'] = userinput['FIRST_NAME'] if 'FIRST_NAME' in userinput else current_user_df.FIRST_NAME.tolist()[0]
            sendData['LAST_NAME'] = userinput['LAST_NAME'] if 'LAST_NAME' in userinput else current_user_df.LAST_NAME.tolist()[0]

            # Update secure user table with data:
            self.__cursor__.execute(self.updateCurator, sendData)
            print('[Info] Changes to CURATOR table has been submitted.')
            
            
        # If email, first name or last name is changed, update event type table:
        if 'LAST_NAME' in userinput:
            sendData = {
                'OLD_LAST_NAME' : current_user_df.LAST_NAME.tolist()[0],
                'ACTION' : userinput['LAST_NAME'],
                'TRANSLATED_EVENT' : 'Study curator set to ' + userinput['LAST_NAME'], 
                'EVENT_TYPE' : 'STUDY_CURATOR_ASSIGNMENT_' + userinput['LAST_NAME'].upper()
            }

            # Update secure user table with data:
            self.__cursor__.execute(self.updateEventType, )
            print('[Info] Changes to EVENT_TYPE table has been submitted.')
            
            
        # If all looked good commit changes:
        self.__commit()
        print('[Info] Changes successfully commited.')
        
    def inactivateUser(self, userinput):
        # Testing user email 1:
        if not self.checkUser(userinput['userEmail']):
            print('[Error] User with %s email does not exist in the database. Exiting.' % userinput['userEmail'])
            exit()

        # Testing user email 2:
        if not self.checkUser(userinput['adminEmail']):
            print('[Error] Administrator with %s email does not exist in the database. Exiting.' % userinput['adminEmail'])
            exit()
            
        # Updating hash:
        self.__cursor__.execute(self.inactivateUserSQL, {'userEmail': userinput['userEmail'], 
                                                 'adminEmail' : userinput['adminEmail']})
        self.__commit()

    def __commit(self):
        self.__connection__.commit()

    def checkUser(self, userEmail):
        df = pd.read_sql(self.checkUserSQL, self.__connection__, params = {'email': userEmail})
        
        self.actual_user = userEmail
        self.actual_user_data = df 
        
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
    userinput['firstName'] = input("Specify first name: ")
    userinput['lastName'] = input("Specify last name: ")
    userinput['emailAddress'] = input("Specify email address: ")
    userinput['role'] = input("Specify role (admin/curator): ")
    userinput['passwordHash'] = input("Specify password hash: ")

    # Adding role ID:
    userinput['roleid'] = '10057973' if userinput['role'] == 'curator' else '10057972'

    # Adding user:
    dbManager.addUser(userinput)

def modifyUser(dbManager):

    # Get the details:
    currentEmail = input("Specify the email address of the user to be updated: ")

    if not currentEmail:
        print('[Error] The current email address needs to be provided! Exiting.')
        exit()

    # Fetch user data:
    if not dbManager.checkUser(currentEmail):
        print('[Error] The specified email address could not be found in the database! Exiting.')
        exit()

    # Save details for the current user:
    current_user_df = dbManager.actual_user_data

    print("[Info] Modification user information of the GWAS Catalog")
    print("[Info] Those fields you want to keep the same, leave empty!")

    # Asking for the parameters:
    userinput = {}
    userinput['EMAIL'] = input("Specify email address: ")

    # At first we have to test if the new email is already in the database:
    if userinput['EMAIL'] and dbManager.checkUser(userinput['EMAIL']):
        print('[Error] The specified email address is already in the database! Exiting.')
        exit()

    # Ask for the first name:
    userinput['FIRST_NAME'] = input("Specify first name ({}): ".format(current_user_df.FIRST_NAME.tolist()[0]))

    # Ask for last name:
    userinput['LAST_NAME'] = input("Specify last name ({}): ".format(current_user_df.LAST_NAME.tolist()[0]))

    # Ask for the password hash:
    userinput['PASSWORD_HASH'] = input("Specify password hash: ")

    # Filter out unused keys:
    userinput = {key : value for key, value in userinput.items() if value}

    # Submit data to update db:
    dbManager.updateUserInfo(currentEmail, userinput)


def inactivateUser(dbManager):
    print("[Info] Inactivating a user of the curation interface.")
    print("[Info] The following information is required to make the modification:")

    # Asking for the parameters:
    userinput = {}
    userinput['userEmail'] = input("Specify e-mail of the user to be inactivated: ")
    userinput['adminEmail'] = input("Specify e-mail of a admin user: ")

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



