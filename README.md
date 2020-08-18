# gwas-utils

This repository is a collection for scripts and small applications we are using in the everyday life of the [GWAS Catalog](http://www.ebi.ac.uk/gwas).

For detailed description of the content of this repository see the individual readme files within each folder or the documentation on [Confluence](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/GWAS+Catalog+tools+and+scripts). 

## Contents

### [Plotter scripts](https://github.com/EBISPOT/gwas-utils/tree/master/catalogPlots)

A collection of scripts we use to generate plots, stats of the GWAS Catalog. 

### [Curator user manager](https://github.com/EBISPOT/gwas-utils/tree/master/curatorUserManager)

A tool to add, change, remove curator user in the database.

### [Data release QC tool](https://github.com/EBISPOT/gwas-utils/tree/master/dataReleaseQC)

Tool to compare databases and solr as part of the quality control process. This script is called during the data release process.

### [Data export tool](https://github.com/EBISPOT/gwas-utils/tree/master/data_export)

A script to perform the data export task of the data release plan. Generates all downloadable files, names them properly, then generates release specific readme for the ftp folder.

### [Diagram creator for data release](https://github.com/EBISPOT/gwas-utils/tree/master/diagramCreator)

A tool to solve issues with diagram generation: when the pussycat application is called, this script keeps checking the process and the generation of the diagram. Also performs certain checks. This script is also part of the data release process.

### [Summary statistics folder manager](https://github.com/EBISPOT/gwas-utils/tree/master/ftpSummaryStatsScript)

Tool to release summary stats folders to ftp. This script is called during the data release process.

### [Access log analysis](https://github.com/EBISPOT/gwas-utils/tree/master/log-analysis)

Scripts to analyse site access logs to generate statistics on user behaviour. 

### [Remapper manager](https://github.com/EBISPOT/gwas-utils/tree/master/remapper_manager)

Upon every new release of Ensembl the full GWAS Catalog data has to be remapped to the new release. This tool to help the remapping process by automating the process that triggers remapping. 

### [Search term classifier](https://github.com/EBISPOT/gwas-utils/tree/master/search_term_classifier)

To generate site access stats it is useful to know what users are sarching for. This script classifies search terms parsed out from site access statistics.

### [Solr wrapper](https://github.com/EBISPOT/gwas-utils/tree/master/solrWrapper)

This small Python module makes it easy to query, update, refresh the specified solr instance/core. 


### [Harmonisation Utils](https://github.com/EBISPOT/gwas-utils/tree/master/harmonisationUtils)

Scripts to control data flow from submission app to harmonisation pipeline
