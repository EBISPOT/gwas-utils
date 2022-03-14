# GWAS Curation Utils
Scripts to help enhance GWAS curation tasks.

Additional details can also be found in the (GWAS Confluence)[https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/GWAS+Curation+Utility+Scripts] page.

These all require direct access to the curation database - for information on this, consult the confluence docs.

## Reported Traits

### Description: 
This script is desiged for curators to be able to get a file of all existing reported traits from the database, analyze a file of curator provided reported traits to find existing similar reported traits in the database, and to be able to submit a batch of reported traits into the database.
(Status as of Aug 2020)

### Usage
```
analyze-reported-traits --help
usage: analyze-reported-traits [-h] [--action ACTION]
                               [--curation_db CURATION_DB]

optional arguments:
  -h, --help            show this help message and exit
  --action ACTION       Task to perform, e.g. dump, analyze, upload
  --curation_db CURATION_DB
                        Name of the database for extracting study data.

```

The `--action` options are:
- `dump` - creates a file of all existing reported traits from the database. The file is saved at the location the script is run and is named "reported_trait.csv"
- `analyze` - reads in a text file of reported traits, analyzes each trait against all existing traits in the database, and then saves the results as a file in the location the script is run named "similarity_analysis_results.csv"
- `upload` - reads in a text file of reported traits and loads these into the database

## Study and Sample Review 

This script provides all information needed for Curation (Level 2) review in a single spreadsheet. 
The script generates the data for all studies given a PubmedId and includes the study design and sample information. See the (GWAS Confluence)[https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/GWAS+Curation+Utility+Scripts] site for more details on the script and it's usage.

### Usage 
```
study-design-sample-info --help
usage: study-design-sample-info [-h] [--database {SPOTPRO}] [--pmid PMID]
                                [--ancestry {collapsed,expanded}]
                                [--username USERNAME]

optional arguments:
  -h, --help            show this help message and exit
  --database {SPOTPRO}  Run as (default: SPOTPRO).
  --pmid PMID           Add Pubmed Identifier, e.g. 28256260.
  --ancestry {collapsed,expanded}
                        Run as (default: collapsed).
  --username USERNAME   Run as (default: gwas-curator).
```

## Curation queue with ancestry info

Script queries the database and produces a report, data_queue_<TIMESTAMP>.csv, which is then emailed to the `--emailRecipient`.
To be setup as a cron task.

```
curation-queue --help
usage: curation-queue [-h] [--database {dev3,spotpro}]
                      [--emailRecipient EMAILRECIPIENT]
                      [--emailFrom EMAILFROM]

optional arguments:
  -h, --help            show this help message and exit
  --database {dev3,spotpro}
                        Run as (default: spotpro).
  --emailRecipient EMAILRECIPIENT
                        Email address where the notification is sent.
  --emailFrom EMAILFROM
                        Email address where the notification is from.
```

## Data curation snapshot

Script (previously known as data_snapshot-GOCI-2181.py) queries the database and produces/appends a report, which is then emailed to the `--emailRecipient`.
To be setup as a cron task.

```
data-curation-snapshot --help
usage: data-curation-snapshot [-h] [--database {dev3,spotpro}]
                              [--mode {debug,production}]
                              [--emailRecipient EMAILRECIPIENT]
                              [--emailFrom EMAILFROM] [--outfile OUTFILE]

optional arguments:
  -h, --help            show this help message and exit
  --database {dev3,spotpro}
                        Database to use
  --mode {debug,production}
                        Run as (default: debug).
  --emailRecipient EMAILRECIPIENT
                        Email address where the notification is sent.
  --emailFrom EMAILFROM
                        Email address where the notification is from.
  --outfile OUTFILE     Name of the report filename
```