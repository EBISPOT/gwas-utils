# Releasing summary statistics to ftp

A Python script to copy summary statistics files from the staging folders to the ftp area. The script is integrated into the GWAS Catalog data release plan. 

### What it does

* Folders in the staging area follow this pattern: `{Author}_{PMID}_{ACCESSIONID}` for published studies, and `{Author}_{PMID}_{STUDYID}` for studies waiting for publishing. 
* Upon data release, the script checks if we get a list of all published studies with summary statistics and try to match them on the staging area and copy them to the ftp are if they are not yet there.
* The script identifies the pattern the folder follows and when it neccessary it renames from `{Author}_{PMID}_{STUDYID}` to `{Author}_{PMID}_{ACCESSIONID}`.
* It copies all folders to the ftp area that not yet there.
* Removes summary statistics from the ftp area of unpublished studies or where the summary statitics are revoked.
* At the end of the process the script sends a detailed report to the defined email address about the actions taken and the missing folders.

### Usage

```bash
python ftp_data_release.py --releaseDB ${database} --stagingDir ${stagingDir} --ftpDir ${ftpDir} --emailRecipient ${email}
```

**Parameters:**

* *releaseDB* : instance name for the release database. This instance should only contain published studies
* *stagingDir* : directory where curators copy summary stats files until the corresponding study is published
* *ftpDir* : directory where the released data will be copyied

### More information

For more information see [confluence page](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/ftpSummaryStatsScript).


