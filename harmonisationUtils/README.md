# Harmonisation Utils

## Harmonisation queuer
This is a CLI app for storing the state of the summary statistics and managing harmonisation queue(s).


### Command overview
```
$ queue-harmonisation --help
usage: queue-harmonisation [-h] --action
                           {refresh,release,rebuild,status,update,harmonised_list}
                           [--study [STUDY [STUDY ...]]] [--priority {1,2,3}]
                           [--source_dir SOURCE_DIR]
                           [--harmonisation_dir HARMONISATION_DIR]
                           [--ftp_dir FTP_DIR] [--number NUMBER]
                           [--harmonisation_type {v1,v0,not_harm}]
                           [--is_harmonised] [--in_progress]

optional arguments:
  -h, --help            show this help message and exit
  --action {refresh,release,rebuild,status,update,harmonised_list}
                        refresh: update the harmonisation queue with newly
                        submitted studies; release: release the next batch of
                        files from the queue; rebuild: rebuild the entire
                        harmonisation queue based on the files on the file
                        system; status: get the status of a list of studies;
                        update: add/update a list of studies; harmonised_list:
                        list of harmonised studies
  --study [STUDY [STUDY ...]]
                        Specific study accession ids.
  --priority {1,2,3}    Set the priority for a study
  --source_dir SOURCE_DIR
                        Path to source directory.
  --harmonisation_dir HARMONISATION_DIR
                        Path to harmonisation directory.
  --ftp_dir FTP_DIR     Path to ftp dir
  --number NUMBER       Number of files to harmonise
  --harmonisation_type {v1,v0,not_harm}
                        harmonisation type
  --is_harmonised       Is harmonised
  --in_progress         Is in progress
```

### Initialise the database (for storing the state)
Background:
- New summary statistics files are put on the staging path (SOURCE_DIR).
- Harmonised summary statistics files are put on the FTP path (FTP_DIR).
- We need to read these file systems to understand which files we have and which files have already been harmonised.
- This is what `--action rebuild` does.

To "rebuild", i.e. create the initial state in the form of a sqlite database (hq.db), run the following command. This only needs to be run once. Once you have the hq.db, you do not need to keep rebuilding it.
  
```
queue-harmonisation --action rebuild  --source_dir SOURCE_DIR --ftp_dir FTP_DIR --harmonisation_dir HARMONISATION_DIR
```

- _Note: HARMONISATION_DIR is the path for where the harmoniation pipeline will read files from. This is not strictly required for the rebuild action_

### Release files to the harmonisation pipeline (intended to be run daily)

This action copies the next X number of files matching the specified to the HARMONISATION_DIR folder, so they can be harmonised. It then, sets thoses study's statuses to "in progress".

```
queue-harmonisation --action release --source_dir SOURCE_DIR --ftp_dir FTP_DIR --harmonisation_dir HARMONISATION_DIR --number INT  --harmonisation_type v1
```

### Refresh database (intended to be run daily)

This action refreshes an existing database with the current state of the summary statistics. This only looks for files since the last time the refresh (or rebuild) was made.

```
queue-harmonisation --action refresh --source_dir SOURCE_DIR --ftp_dir FTP_DIR --harmonisation_dir HARMONISATION_DIR
```

### Get the status of a study

Get the status (record from database, see Study data model below) for a study.
```
queue-harmonisation --action status --study <GCST>
```

### Manually update a study in the database
This can be used to manually set the properties of the Study. e.g. Set to high priority:
```
queue-harmonisation --action update --study <GCST> --priority 1
```
_Note: that is_harmonised and in_progress set to True if they are provided and, therefore, if they are not provided, those properties will be set to False_.

### Data model
```
class Study:
    """Class for study harmonisation status."""
    study_id: str
    harmonisation_type: HarmonisationType = HarmonisationType.NOT_TO_HARMONISE.value
    is_harmonised: bool = False
    in_progress: bool = False
    priority: Priority = Priority.MED.value
```

