import pandas as pd
import sys
import os
import argparse
import subprocess
from subprocess import Popen, PIPE
from datetime import date
import re
import hashlib
import shutil

from gwas_db_connect import DBConnection

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
                        WHERE S.PUBLICATION_ID = P.ID 
                            AND P.FIRST_AUTHOR_ID = A.ID 
                            AND S.HOUSEKEEPING_ID = H.ID 
                            AND S.FULL_PVALUE_SET = 1 
                            AND H.IS_PUBLISHED = 1 
                      '''
    # may need to query unpublished study table as well
    extractPrePubSql = '''SELECT U.ACCESSION 
                        FROM UNPUBLISHED_STUDY U 
                        WHERE U.SUMMARY_STATS_FILE <> 'NR'
                       '''

    # Query to fetch study related info to find out why a folder is unexpected:
    extractStudyInfo = '''
        SELECT REPLACE(A.FULLNAME_STANDARD, ' ', '') AS AUTHOR,
          P.PUBMED_ID,
          S.ACCESSION_ID,
          S.FULL_PVALUE_SET,
          HK.IS_PUBLISHED,
          HK.CATALOG_UNPUBLISH_DATE
        FROM STUDY S,
            HOUSEKEEPING HK,
            PUBLICATION P,
            AUTHOR A
        WHERE ACCESSION_ID in ({})
          AND HK.ID = S.HOUSEKEEPING_ID
          AND S.PUBLICATION_ID = P.ID
          AND P.FIRST_AUTHOR_ID = A.ID
    '''

    stagingFoldersToRename = [] # folders with study IDs in the staging area that will be renamed
    stagingNotExpectedFolders = [] # Folders in the staging area that are not expected to be there
    stagingMissingFolders = [] # Folders missing from the staging area based on the database
    ftpFoldersToRemove = [] # Folders in the ftp area that needs to be removed
    ftpExpectedFolders = [] # Expected folders in the ftp area
    foldersToCopy = [] # Folders that will be copied from the staging area to the ftp area

    def __init__(self, connection, stagingDir, ftpDir, database):
        self.stagingDir = stagingDir
        self.ftpDir = ftpDir
        self.database = database
        try:
            df = pd.read_sql(self.extractStudySql, connection)
            df = df.append(prepub_df)
        except:
            print('exception')

        # Set study IDs as string:
        #df['ID'] = df['ID'].astype(str)

        # Function to generate folder names:
        def _generateFolder(row):
            return("_".join(row[[0,1,2]]) if not row[2] is None else 'NA')

        # Generate folder names with accession IDs and study IDs:
        df['newFolderName'] = df[['AUTHOR','PUBMED_ID', 'ACCESSION_ID']].apply(_generateFolder, axis=1)
        
        prepub_df = pd.read_sql(self.extractPrePubSql, connection).rename(columns={'ACCESSION':'ACCESSION_ID'})
        prepub_df['newFolderName'] = prepub_df['ACCESSION_ID']

        # identify any studies that are present in both the unpublished study and published study tables 
        # (this should never happen, but it does) and assume they should not be in the unpublished table
        self.unpubAndPubConflict = prepub_df[prepub_df['ACCESSION_ID'].isin(df['ACCESSION_ID'])]['ACCESSION_ID'].tolist()
        prepub_df = prepub_df[~prepub_df['ACCESSION_ID'].isin(df['ACCESSION_ID'])]

        df = df.append(prepub_df)
        df['oldFolderName'] = df[['ACCESSION_ID']]

        # Print out report:
        print('[Info] Based on the release database ({}) {} studies have summary stats from {} publication'.format(database, len(df), len(df.PUBMED_ID.unique())))
        
        self.DBstudies = df

    def checkStagingArea(self, stagingFolders):

        # Folders that have names with accession ID are expected to be copied to the ftp area:
        self.ftpExpectedFolders = stagingFolders.loc[stagingFolders.isin(self.DBstudies.newFolderName)].tolist()

        # Find out which folders needs to be renamed or unexpected: folders with accession ID could not be found
        for problematicFolder in stagingFolders[~stagingFolders.isin(self.DBstudies.newFolderName)]:
            
            # Folders with study ID could be found -> to rename then copy
            if self.DBstudies.oldFolderName.isin([problematicFolder]).any():
                self.stagingFoldersToRename.append((problematicFolder, self.DBstudies.loc[self.DBstudies.oldFolderName == problematicFolder,'newFolderName'].any()))
                self.ftpExpectedFolders.append(self.DBstudies.loc[self.DBstudies.oldFolderName == problematicFolder,'newFolderName'].any())

            # Folders cannot be found -> not expected folder or file.
            else:
                self.stagingNotExpectedFolders.append(problematicFolder)

        # Folders we don't see but expect:
        self.stagingMissingFolders = self.DBstudies.newFolderName[(~self.DBstudies.newFolderName.isin(stagingFolders) & 
                                                                   ~self.DBstudies.oldFolderName.isin(stagingFolders))].tolist()
                
    def checkFtpArea(self, ftpFolders):

        # Check folders on ftp that should not be there:
        self.ftpFoldersToRemove = ftpFolders.loc[~ftpFolders.isin(self.DBstudies.newFolderName)].tolist()

        # Need to keep unpublished links so these do not need to be removed
        self.ftpFoldersToRemove = [f for f in self.ftpFoldersToRemove if not str(f.startswith("GCST"))]

        # Check folders on staging that should be copied to ftp:
        allExpectedFolders = pd.Series(self.ftpExpectedFolders)
        self.foldersToCopy = allExpectedFolders[~allExpectedFolders.isin(ftpFolders)].tolist()

    def generateReport(self, exceptions=[]):
        today = date.today()

        # Header of the report:
        reportString = ('This is a report on the daily summary statistics release\n\n'
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
        if len(self.stagingMissingFolders):
            reportString += '\n\n[Info] The following folders were missing from the staging area:\n'
            reportString += "\n".join(map('\t{}'.format,self.stagingMissingFolders))
        else:
            reportString += '\n\n[Info] No folder is missing from the staging directory.\n'
        
        # Unexpected folders in the staging area:
        if len(self.stagingNotExpectedFolders):
            reportString += '\n\n[Info] The following folders in the staging area are unexpected or not yet published:\n'
            reportString += "\n".join(map('\t{}'.format,self.stagingNotExpectedFolders))
        else:
            reportString += '\n\n[Info] No unexpected folder is found in the staging directory.\n'

        # Unexpected folders in the ftp area:
        if len(self.ftpFoldersToRemove):
            self.__check_outstanding_studies()
            reportString += '\n\n[Info] The following folders are unexpected in the ftp area:\n'
            reportString += "\n".join(map('\t{}'.format,self.ftpFoldersToRemove_w_comments))
        else:
            reportString += '\n\n[Info] All folders in the ftp directory looks good.\n'

        # Studies in both the unpublished and published study tables:
        if len(self.unpubAndPubConflict):
            reportString += '\n\n[Info] The following studies were identified in both the UNPUBLISHED_STUDY and (published) STUDY tables:\n'
            reportString += "\n".join(map('\t{}'.format,self.unpubAndPubConflict))

        if len(exceptions):
            reportString += '\n\n[Error] The following exceptions were raised:\n'
            reportString += "\n".join(map('\t{}'.format,exceptions))


        return(reportString)

    # This function parses folder names to return accession IDs:
    def __extract_study_accessions(self, folderList):
        accessionIdPattern = '(GCST\d+)$'

        accessionIDs = []
        for folder in folderList:
            matches = re.findall(accessionIdPattern, folder, flags=0)
            if matches:
                accessionIDs.append(matches[0])

        return(accessionIDs)

    # This function checks why certain folders are unexpected in the ftp folder:
    def __check_outstanding_studies(self):

        # Retrieve all problematic study:
        accessionIDs = self.__extract_study_accessions(self.ftpFoldersToRemove)
        quoted_ids = ["'{}'".format(x) for x in accessionIDs]
        outstandingStudies = pd.read_sql(self.extractStudyInfo.format(','.join(quoted_ids)), connection)

        # Generate folder name:
        if len(outstandingStudies) > 0:
            outstandingStudies['folder'] = outstandingStudies.apply(lambda x: '{}_{}_{}'.format(x['AUTHOR'],x['PUBMED_ID'],x['ACCESSION_ID']) if all([x['AUTHOR'], x['PUBMED_ID']]) else x['ACCESSION_ID'], axis = 1)
        else:
            outstandingStudies['folder'] = 'NA'

        ftpFoldersToRemove_w_comments = []
        for folder in self.ftpFoldersToRemove:

            # If study could not be extracted from the database:
            if not outstandingStudies.folder.isin([folder]).any():
                ftpFoldersToRemove_w_comments.append('{} - not found in the database'.format(folder))
                continue
            
            # Let's take just one row:
            row = outstandingStudies.loc[outstandingStudies.folder == folder].iloc[0]
            
            # The study was unpublished:
            if not pd.isna(row['CATALOG_UNPUBLISH_DATE']):
                ftpFoldersToRemove_w_comments.append('{} - study was unpublished on: {:%Y %b %d}'.format(folder, row['CATALOG_UNPUBLISH_DATE']))

            # The summary stats were retracted:    
            elif row['FULL_PVALUE_SET'] == 0:
                ftpFoldersToRemove_w_comments.append('{} - the summary stats for this study is retracted.'.format(folder))

            # The study is not published, but is not retracted either:
            elif row['IS_PUBLISHED'] == 0:
                ftpFoldersToRemove_w_comments.append('{} - the study is not published.'.format(folder))
         
            # Unknown reason:
            else:
                ftpFoldersToRemove_w_comments.append('{} - the study state is not known. It seems the folder should be there.'.format(folder))

        self.ftpFoldersToRemove_w_comments = ftpFoldersToRemove_w_comments


exceptions = []

def renameFolders(folders,stagingDir):
    for folder in folders:
        oldFolder = os.path.join(stagingDir, folder[0])
        newFolder = os.path.join(stagingDir, folder[1])
        try:
            shutil.move(oldFolder, newFolder)
        except shutil.Error as e:
            exceptions.append(e)
            print('yes')
            print(exceptions)

def copyFoldersToFtp(folders, sourcePath, targetPath):

    for folderToCopy in folders:

        # Copy directory to ftp area:
        from_dir = os.path.join(sourcePath, folderToCopy)
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
            exceptions.append(e)

def generate_md5_sum(folder):
    '''
    This function will generate md5sums for all files in the provided folder
    and save in the same folder.
    '''
    # Get list of files in a folder:
    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    
    # Check if any of the files looks like an md5 checksum file, we then skipping:
    for file in onlyfiles:
        if 'md5' in file.lower():
            return None

    # md5checksums are stored:
    md5checksums = []
    
    # Loopthrough the files and calculate md5sum:
    for filename in onlyfiles:
        #print('md5 for ' + filename)
        with open(os.path.join(folder,filename),"rb") as f:
            # Read and calculate hash:
            #bytes = f.read()
            # read file as bytes
            file_hash = hashlib.md5()
            for chunk in iter(lambda: f.read(8192), b''):
                file_hash.update(chunk)
            md5checksums.append([filename, file_hash.hexdigest()])
    
    # Saving values into a file:
    with open('{}/md5sum.txt'.format(folder), 'w') as writer:
        for file in md5checksums:
            writer.write('{} {}\n'.format(file[1], file[0])) 

def sendEmailReport(report, emailAddresses):
    try:
        mailBody = 'Subject: Summary Stats release report\nTo: {}\n{}'.format(emailAddresses,report)
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi", emailAddresses], stdin=PIPE)
        p.communicate(mailBody.encode('utf-8'))
    except OSError as e:
        print(e)
        exceptions.append(e)

def retractFolderFromFtp(folders, ftpDir):
    for folder in folders:
        folderWPath = os.path.join(ftpDir, folder)
        try:
            subprocess.call(['rm', '-rf', folderWPath])
        except OSError as e:
            print(e) 
            exceptions.append(e)

if __name__ == '__main__':

    # Parsing command line arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument('--releaseDB', type=str, help='Name of the database for extracting study data.')
    parser.add_argument('--stagingDir', type=str, help='Path to staging directory.')
    parser.add_argument('--ftpDir', type=str, help='Path to ftp directory.')
    parser.add_argument('--emailRecipient', type=str, help='Email address where the notification is sent.')
    parser.add_argument('--test', action='store_true', help='If test run is specified, no release is done just send notification.')
    args = parser.parse_args()

    database = args.releaseDB
    stagingDir = args.stagingDir
    ftpDir = args.ftpDir
    emailRecipient = args.emailRecipient
    testFlag = args.test # By default the test flag is false

    # Print out start report:
    print('[Info  {:%d, %b %Y}] Summary stats release started...'.format(date.today()))

    # Check if staging directory exists:
    if not os.path.isdir(stagingDir):
        print('[Error {:%d, %b %Y}] No valid staging directory provided. Exiting.'.format(date.today()))
        sys.exit(1)

    # Check if ftp dir exists:
    if not os.path.isdir(ftpDir):
        print('[Error{:%d, %b %Y}] No valid ftp directory provided. Exiting.'.format(date.today()))
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
    ## When the comparisons are done, we move files, if we are not testing:
    ##

    # Just sending report without action:
    if testFlag:
        report = summaryStatsFoldersObj.generateReport(exceptions)
        sendEmailReport(report, emailRecipient)
        exit(0)

    # Rename folders where study ID is given instead of accession ID
    renameFolders(summaryStatsFoldersObj.stagingFoldersToRename,stagingDir)

    # Generate md5sum checksum for folders to be copied:
    for folder in summaryStatsFoldersObj.foldersToCopy:
        generate_md5_sum('{}/{}'.format(stagingDir,folder))

    # Copy folders to ftp:
    copyFoldersToFtp(summaryStatsFoldersObj.foldersToCopy, stagingDir, ftpDir)

    # # Folders are no longer retracted from ftp:
    # retractFolderFromFtp(summaryStatsFoldersObj.ftpFoldersToRemove, ftpDir)

    if (len(summaryStatsFoldersObj.foldersToCopy) == 0) and \
       (len(summaryStatsFoldersObj.stagingMissingFolders) == 0):
        
        print('[Info {:%d, %b %Y}] There was no study to release and no folder was missing.'.format(date.today()))
        exit(0)

    ##
    ## When all done generate report and send email:
    ##

    # Generate report if at least one study is released:
    report = summaryStatsFoldersObj.generateReport(exceptions)
    # Send email about the report:
    sendEmailReport(report, emailRecipient)

