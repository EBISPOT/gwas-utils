import pandas as pd
import sys
import os
import argparse
import subprocess
from subprocess import Popen, PIPE
from datetime import date

import gwas_data_sources
import DBConnection

'''
Applied nomenclature:
    * Staging area - folder for summary stats deposition 
                     while study is not published and released.
    * Ftp area - summary stats files are copied from staging to this 
                 directory then automatically synced with the live ftp 
'''

class summaryStatsFolders(object):

    # This query will return all studies with summary stats:
    extractStudySql = '''SELECT DISTINCT S.ID, REPLACE(A.FULLNAME_STANDARD, ' ', '') AS AUTHOR,
                            P.PUBMED_ID, S.ACCESSION_ID, H.IS_PUBLISHED
                        FROM STUDY S, PUBLICATION P, HOUSEKEEPING H, AUTHOR A 
                        WHERE S.PUBLICATION_ID = P.ID and P.FIRST_AUTHOR_ID = A.ID 
                            and S.HOUSEKEEPING_ID = H.ID 
                            and S.FULL_PVALUE_SET = 1 
                      '''

    stagingFoldersToRename = [] # folders with study IDs in the staging area that will be renamed
    stagingNotExpectedFolders = [] # Folders in the staging area that are not expected to be there
    stagingMissingFolders = [] # Folders missing from the staging area based on the database
    stagingNotYetPublished = [] # Folders in the staging area that are not yet publised
    ftpFoldersToRemove = [] # Folders in the ftp area that needs to be removed
    ftpExpectedFolders = [] # Expected folders in the ftp area
    foldersToCopy = [] # Folders that will be copied from the staging area to the ftp area

    def __init__(self, connection, stagingDir, ftpDir, database):
        self.stagingDir = stagingDir
        self.ftpDir = ftpDir
        self.database = database
        try:
            df = pd.read_sql(self.extractStudySql, connection)
        except:
            print('exception')

        # Set study IDs as string:
        df['ID'] = df['ID'].astype(str)

        # Function to generate folder names:
        def _generateFolder(row):
            return("_".join(row[[0,1,2]]) if not row[2] is None else 'NA')

        # Generate folder names with accession IDs and study IDs:
        df['newFolderName'] = df[['AUTHOR','PUBMED_ID', 'ACCESSION_ID']].apply(_generateFolder, axis = 1)
        df['oldFolderName'] = df[['AUTHOR','PUBMED_ID', 'ID']].apply(_generateFolder, axis = 1)
        
        # Print out report:
        print('[Info] Based on the database {} studies have summary stats from {} publication'.format(len(df), len(df.PUBMED_ID.unique())))
        print('[Info] Currently {} studies not yet published.'.format(len(df.loc[ df.IS_PUBLISHED == 0])))
        
        self.DBstudies = df

    def checkStagingArea(self, stagingFolders):

        # Folders that have names with accession ID are expected to be copied to the ftp area:
        self.ftpExpectedFolders = stagingFolders.loc[stagingFolders.isin(self.DBstudies.newFolderName)].tolist()

        # Find out which folders needs to be renamed or unexpected: folders with accession ID could not be found
        for problematicFolder in stagingFolders[~stagingFolders.isin(self.DBstudies.newFolderName)]:
            
            # Folders with study ID could be found and study is published -> to rename then copy
            if (self.DBstudies.oldFolderName.isin([problematicFolder]).any() and
              self.DBstudies.loc[self.DBstudies.oldFolderName == problematicFolder,'IS_PUBLISHED'].any() != 0):
                self.stagingFoldersToRename.append((problematicFolder, self.DBstudies.loc[self.DBstudies.oldFolderName == problematicFolder,'newFolderName'].any()))
                self.ftpExpectedFolders.append(self.DBstudies.loc[self.DBstudies.oldFolderName == problematicFolder,'newFolderName'].any())

            # Folders with study ID could be found but study is not published -> not yet published
            elif self.DBstudies.oldFolderName.isin([problematicFolder]).any():
                self.stagingNotYetPublished.append(problematicFolder)
            
            # Folders cannot be found anywhere -> not expected folder or file.
            else:
                self.stagingNotExpectedFolders.append(problematicFolder)

        # Folders we don't see but expect:
        expectedStudies = self.DBstudies.loc[self.DBstudies.IS_PUBLISHED == 1]
        for missingFolder in expectedStudies.newFolderName[~expectedStudies.newFolderName.isin(stagingFolders)]:
            
            # The folder is not named with study ID -> missing folder:
            if not stagingFolders.isin(expectedStudies.loc[expectedStudies.newFolderName == missingFolder, 'oldFolderName']).any():
                self.stagingMissingFolders.append(missingFolder)
                
    def checkFtpArea(self, ftpFolders):

        # Check folders on ftp that should not be there:
        self.ftpFoldersToRemove = ftpFolders.loc[~ftpFolders.isin(self.DBstudies.newFolderName)].tolist()

        # Check folders on staging that should be copied to ftp:
        allExpectedFolders = pd.Series(self.ftpExpectedFolders)
        self.foldersToCopy = allExpectedFolders[~allExpectedFolders.isin(ftpFolders)].tolist()

    def generateReport(self):
        today = date.today()

        # Header of the report:
        reportString = ('This is a report on summary statistics data release\n\n'
                       '[Info] Date of run: {:%d, %b %Y}\n'
                       '[Info] Source database: {}\n'
                       '[Info] Staging area: {}\n'
                       '[Info] Ftp area: {}\n'
                       ''.format(today,self.database,self.stagingDir,self.ftpDir))

        # Released summary stats:
        reportString += '\n[Info] This round summary statistics of {} studies were released.\n'.format(len(self.foldersToCopy))
        reportString += "\n".join(map('\t{}'.format,self.foldersToCopy))

        # Renamed folders:
        reportString += '\n\n[Info] The following folders were renamed in the staging area:\n'
        reportString += '\n'.join(map(lambda x:'\t{} -> {}'.format(*x), summaryStatsFoldersObj.stagingFoldersToRename))

        # Missing folders from the staging area:
        reportString += '\n\n[Info] The following folders were missing from the staging area:\n'
        reportString += "\n".join(map('\t{}'.format,self.stagingMissingFolders))
        
        # Not yet published studies:
        reportString += '\n\n[Info] The following {} folders in the staging area are not yet published:\n'.format(len(self.stagingNotYetPublished))
        reportString += "\n".join(map('\t{}'.format,self.stagingNotYetPublished))
        
        # Unexpected folders in the staging area:
        reportString += '\n\n[Info] The following folders in the staging area are unexpected:\n'
        reportString += "\n".join(map('\t{}'.format,self.stagingNotExpectedFolders))
        
        # Removed folders in the ftp area:
        reportString += '\n\n[Info] The following folders were removed from the ftp area:\n'
        reportString += "\n".join(map('\t{}'.format,self.ftpFoldersToRemove))
        
        return(reportString)

def renameFolders(folders,stagingDir):
    for folder in folders:
        oldFolder = '{}/{}'.format(stagingDir, folder[0])
        newFolder = '{}/{}'.format(stagingDir, folder[1])
        try:
            subprocess.call(['mv', oldFolder, newFolder])
        except OSError as e:
            print(e)

def copyFoldersToFtp(folders, sourcePath, targetPath):

    for folderToCopy in folders:

        # Copy directory to ftp area:
        from_dir = '{}/{}'.format(sourcePath, folderToCopy)
        to_dir = '{}/'.format(targetPath)
        
        try:
            print('[Info] Copying {} from staging to production'.format(folderToCopy))
            
            # rsync parameters:
            # -r - recursive
            # -v - verbose
            # -h - human readable output
            # --size-only - only file size is compared, timestamp is ignored
            # --delete - delete outstanding files on the target folder
            # --exclude=harmonised - excluding harmonised folders
            # --exclude=".*" - excluding hidden files
            subprocess.call(['rsync', '-rvh','--size-only', '--delete', '--exclude=harmonised', '--exclude=.*', from_dir, to_dir])
        except OSError as e:
            print(e)

def sendEmailReport(report, emailAddress):
    try:
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi", emailAddress], stdin=PIPE)
        p.communicate(b'Subject: Summary Stats release report\n' + report.encode('utf-8'))
    except OSError as e:
        print(e) 

def retractFolderFromFtp(folders, ftpDir):
    for folder in folders:
        folderWPath = '{}/{}'.format(ftpDir, folder)
        try:
            subprocess.call(['rm', '-rf', folderWPath])
        except OSError as e:
            print(e) 

if __name__ == '__main__':

    # Parsing command line arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', type=str, help='Name of the database for extracting study data.')
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--ftpDir', type=str, help='Path to ftp directory.')
    parser.add_argument('--emailRecipient', type=str, help='Email address where the notification is sent.')
    args = parser.parse_args()

    database = args.database
    stagingDir = args.stagingDir
    ftpDir = args.ftpDir
    emailRecipient = args.emailRecipient

    # Check if staging directory exists:
    if not os.path.isdir(stagingDir):
        print('[Error] No valid staging directory provided. Exiting.')
        sys.exit(1)

    # Check if ftp dir exists:
    if not os.path.isdir(ftpDir):
        print('[Error] No valid ftp directory provided. Exiting.')
        sys.exit(1)

    # Open connection:
    db_object = DBConnection.gwasCatalogDbConnector(database)
    connection = db_object.connection

    # Get folders from the staging area:
    stagingFolders = pd.Series(os.listdir(stagingDir))

    # Get folders from the ftp area:
    ftpFolders = pd.Series(os.listdir(ftpDir))

    # Extracting studies with summary stats from the database:
    summaryStatsFoldersObj = summaryStatsFolders(connection, stagingDir, ftpDir, database)

    # Compare expected folders with the staging area:
    summaryStatsFoldersObj.checkStagingArea(stagingFolders)

    # Compare expected folders with the ftp area:
    summaryStatsFoldersObj.checkFtpArea(ftpFolders)

    ##
    ## When the comparisons are done, we move files:
    ##

    # Rename folders where study ID is given instead of accession ID
    renameFolders(summaryStatsFoldersObj.stagingFoldersToRename,stagingDir)

    # Copy folders to ftp:
    copyFoldersToFtp(summaryStatsFoldersObj.foldersToCopy, stagingDir, ftpDir)

    # Remove folders from ftp:
    retractFolderFromFtp(summaryStatsFoldersObj.ftpFoldersToRemove, ftpDir)

    ##
    ## When all done generate report and send email:
    ##

    # Generate report:
    report = summaryStatsFoldersObj.generateReport()

    # Send email about the report:
    sendEmailReport(report, emailRecipient)

