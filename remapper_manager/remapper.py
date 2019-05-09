import pandas as pd
import json
import requests
import argparse 

# Handler for database:
from functions import databaseManipulation


# Get Ensembl version
def getEnsemblRelease():
    URL = 'https://rest.ensembl.org/info/data/?content-type=application/json'
    response = requests.get(URL, headers={ "Content-Type" : "application/json"})
    if not response.ok:
      response.raise_for_status()
      sys.exit()
     
    decoded = response.json()
    return(decoded['releases'][0])

# Restart remapping.
def restartRemapping(ensemblRelease):
    return({'ensemblVersion' : ensemblRelease, 'progression' : [[0,0]]})

def triggerRemapping(dbInstance, progressData, rowCount):

    # Extracting the last stage:
    lastState = progressData['progression'][-1]
    oldStart = lastState[0]
    oldEnd = lastState[1]

    # Print progress:
    print("[Info] The last remapping happened between %s and %s" % (oldStart, oldEnd))

    # Instanciate db object:    
    databaseObject = databaseManipulation.databaseManipulation(dbInstance)

    # Get unmapped:
    unmappedCount = databaseObject.getUnmappedCount()
    print("[Info] Number of unmapped associations: %s" % unmappedCount)

    # Get first unmapped:
    firstToRemap = databaseObject.getFirstToRemap(oldStart, oldEnd)
    print("[Info] First association to remap: %s" % firstToRemap)

    # Get the ID of the last association to remap:
    lastToRemap = databaseObject.getLastToRemap(firstToRemap, rowCount)
    print("[Info] The last ID to remap is: %s" % lastToRemap)

    # Get the number of associations that will be remapped:
    countToRemap = databaseObject.getAssociationCount(firstToRemap, lastToRemap)
    print("[Info] Between ID: %s-%s there are %s associations." % (firstToRemap, lastToRemap, countToRemap))

    # Setting associations to unmapped:
    databaseObject.removeMapping(firstToRemap, lastToRemap)

    # Get unmapped:
    unmappedCount = databaseObject.getUnmappedCount()
    print("[Info] Number of unmapped associations after updating database: %s" % unmappedCount)

    # Closing connection:
    databaseObject.closeConnection()

    # Updating the progress file:
    return([firstToRemap, lastToRemap])

if __name__ == '__main__':

    # Get Ensembl version:
    ensemblRelease = getEnsemblRelease()
    print("[Info] Ensembl version fetched from Ensembl RESET API: %s" % ensemblRelease)

    # Parsing command line arguments:
    parser = argparse.ArgumentParser(description='This script was writen to ')
    parser.add_argument('--dbInstanceName', default='dev2', help='Production database.')
    parser.add_argument('--progressFileName', default='progress.json', help='JSON file containing information on the progression of the remapping.')
    parser.add_argument('--remapCount', type = int, help='Number of associations to remap in one round.')

    args = parser.parse_args()

    rowCount = args.remapCount
    dbInstanceName = args.dbInstanceName
    progressFileName = args.progressFileName
    
    # Reaing progress json
    with open(progressFileName) as f:
        progressData = json.load(f)

    # If the newest release is not the same, a new remapping is started:
    if (progressData['ensemblVersion'] != ensemblRelease ):
       print("[Warning] The previously used Ensembl version (e%s) is not matching to the newest Ensembl release (e%s)" %(
            progressData['ensemblVersion'], ensemblRelease))
       progressData = restartRemapping(ensemblRelease)

    # We might want to force remapping even if the ensembl release is good. 
    # if forcedRemapping:
    #    ProgressData = restartRemapping(ensemblRelease)

    # Trigger remapping by changing database entries of a set of associations:
    newIDs = triggerRemapping(dbInstanceName, progressData, rowCount)

    # Adding new IDs to the progression
    progressData['progression'].append(newIDs)

    # Saving progress:
    with open(progressFileName, 'w') as f:  # writing JSON object
       json.dump(progressData, f)

