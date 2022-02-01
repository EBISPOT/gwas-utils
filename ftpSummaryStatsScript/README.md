# Releasing summary statistics to ftp

A Python script to copy summary statistics files from the staging folders to the ftp area. The script is integrated into the GWAS Catalog data release plan. 

### What it does

* Based on the following inputs: staging directory, ftp directory and curation API it decides what needs to be released to ftp or removed (permissions revoked) from the ftp. 
* The API is used to determine if "is_published" AND "full_p_value_set", then if sumstats are on staging AND NOT on ftp --> sync
* What needs to be removed from ftp? --> NOT ("is_published" AND "full_p_value_set") AND ftp --> remove from ftp
* "remove from FTP" means that the permissions are adjusted such that the files cannot be accessed by external users
* A report is generated from what happened and emailed to the `emailRecipient`

### Usage with singularity

```bash
$ singularity exec docker://ebispot/gwas-utils:latest python /ftpSummaryStatsScript/ftp_sync.py --help
usage: ftp_sync.py [-h] [--stagingDir STAGINGDIR] [--ftpDir FTPDIR]
                   [--apiURL APIURL] [--test]
                   [--emailRecipient EMAILRECIPIENT] [--emailFrom EMAILFROM]

optional arguments:
  -h, --help            show this help message and exit
  --stagingDir STAGINGDIR
                        Path to staging directory.
  --ftpDir FTPDIR       Path to ftp directory.
  --apiURL APIURL       URL base for curation REST API
  --test                If test run is specified, no release is done just send
                        notification.
  --emailRecipient EMAILRECIPIENT
                        Email address where the notification is sent.
  --emailFrom EMAILFROM
                        Email address where the notification is from.
```

### More information

For more information see [confluence page](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/ftpSummaryStatsScript).


