# Publication lookup

This script was written for efficiently looking up publications in the GWAS Catalog database. The input data is a txt file containing Pubmed IDs listed in a single column. The output is a tsv file with the following columns: pubmed_id, title, publication_date, journal, first_author, in_catalog, study_accession, summary_stats

## Requirements

Written for `Python 3.6`

Custom Python packages:

 * `gwas_db_connect` : this package help connecting to database instances of the GWAS Catalog [link](https://gitlab.ebi.ac.uk/gwas/gwas_db_connect/commits/master)

Other packages:

* `pandas` : tables are manipulated and compared using pandas dataframes
* `requests` : fetch data from the [EuroPMC REST API](https://europepmc.org/RestfulWebService)
* `urllib.parse` : format request strings
* `collections` : support for ordered dictionaries

## Usage

```bash
python ${scriptDir}/publication_lookup.py \
    --dbInstance ${dbInstance} \
    --input ${input_filename} \
    --queryType pmid \
    --output ${output_filename}
```

**Where**:

* `dbInstance` is the database instance name from which the publications are looked up.
* `input` txt file where each line contains one title or pmid
* `queryType` if the input is a list of Pubmed IDs (`pmid`) or titles (`title`). Default value is `pmid`.
* `output` the filename into which the table is saved in tsv format. Default value: `output.tsv`

