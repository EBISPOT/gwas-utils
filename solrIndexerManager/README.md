# Solr indexer manager

This scripts allows incremental solr indexing to speed up data release. 

## Description

The script takes two database instances, determins the newly added, updated and deleted studies. The updated and deleted studies and associations are deleted from the solr index. All efo traits and disease traits are also deleted from the solr index. The pubmed ID of the newly added and updated studies are passed to the solr indexer application for indexing. 

For a single pubmed ID, a single Nextflow job is started, where only association and study documents are generated. Two jobs are started up to generate efo and disease trait documents. The script keeps track of running jobs and provides a constant update. When all running jobs are finished the script exits. 

**Warning!!**: the sript DOES NOT checks the output status of the jobs. It is not yet implemented as there are downstream QC processed to check the document counts.

## Requirements

Python version: `3.7`

The following custom packages needs to be installed:

 * `solrWrapper` : this package provides tools to manipulate the solr index. [link](https://github.com/EBISPOT/gwas-utils/tree/master/solrWrapper)
 * `gwas_db_connect` : this package help connecting to database instances of the GWAS Catalog [link](https://gitlab.ebi.ac.uk/gwas/gwas_db_connect/commits/master)

Other packages:

* `pandas` : tables are manipulated and compared using pandas dataframes.

## Usage:

```bash
python ${scriptDir}/indexer_manager.py \
    --newInstance ${new_database_instance} \
    --oldInstance ${old_database_instance} \
    --solrHost http://localhost --solrCore gwas --solrPort 8983 \
    --wrapperScript ${wrapperScriptDir}/build-solr-index.sh \
    --logFolder ${logDir} \
    --fullIndex
```

**Where**:

* `new_database_instance` is the database instance name containing the 'new' data
* `old_database_instance` is the database instance name containing the 'old' data
* `solrHost`, `solrCore`, `8983` are pointers to the solr server
* `${wrapperScriptDir}/build-solr-index.sh` is the wrapper for the solr indexer application. (currently not versioned)
* `logDir` directory into which the logfiles are saved.
* `--fullIndex` - Enable this for the full catalog index: if this switch is turned on, the solr index is wiped off, and all publication of the new database instance is submitted to the farm for indexing.
