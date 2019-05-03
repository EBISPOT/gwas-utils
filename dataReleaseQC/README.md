# dataReleaseQC

A tool to perform quality control for the [GWAS Catalog](https://www.ebi.ac.uk/gwas) data release. The script is called after the solr index generation is finished. At the current state it compares the database with the old and new solr indices. 

### Requirements:

The following packages are required:

* [codecs](https://docs.python.org/2/library/codecs.html)
* [pandas](https://pandas.pydata.org)
* [numpy](https://www.numpy.org/)
* [subprocess](https://docs.python.org/2/library/subprocess.html)

The script was written using Python 3.7

### Usage:


```bash
python studyQC.py --oldSolrAddress <solrAddress>  --newSolrAddress <solrAddress> --fatSolrCore <coreName> --document <documentType> --productionDB <instanceName> --releaseDB <instanceName>  --emailAddress <email>
```

Where solr address is specified like: `localhost:8983`

### Behavior:

The script compares study data in release (`releaseDB`), production (`productionDB`) databases with studies already indexed in the old (`oldSolrAddress`) and new (`newSolrAddress`) solr indicies. The results are sent to the specified email address and also saved in a text file (eg. `SolrQC_report_2019-05-01.txt`)
