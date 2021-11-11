# Data export application

As part of the GWAS Catalog data release process we generate a wide-range of downloadable files with associations, studies, ancestries and trait mappings. The generation of these files is an elaborate process of the data release bamboo plan, is now collapsed into one single script.

This application provides extra functionality compared to the original data export process: 
* It collects all published downloadable files including the `.owl` knowledge base files.
* The diagram is also fetched and converted into `.png` and `.pdf` format.
* The downloadable files named to match the naming convention on the [UI download page](https://www.ebi.ac.uk/gwas/docs/file-downloads)
* A readme file is also generated, which provides a description for all files included in the release folder. 
* The readme file contains links to other relevant sources eg. [page describing the column headers](https://www.ebi.ac.uk/gwas/docs/fileheaders).
* The readme file contains md5 checksums for all files to ensure data quality.


## Usage

```bash
Usage: ./data_export/data_export.sh -o <output folder> \
          -e <Ensembl version> \
          -s <mapper folder> \
          -x <tomcat host> \
          -k <knowledge base folder> \
          -d <diagram folder> \
          -r <release file> \
          -h
```

**Where:**

* `<output folder>`   : directory in which the exported files will be generated.
* `<Ensembl version>` : the Ensembl version on which the data is mapped.
* `<mapper folder>`   : where the parent mapper application is hosted.
* `<tomcat host>`     : the server on which the gwas appliation is running with port.
* `<knowledge base folder>` : Folder where the `.owl` knowledge base files are stored.
* `<diagram folder>`        : folders where the diagrams generated.
* `<release file>`          : file with the release notes.

## Output

The following files should be in the output folder after the successful run:

* gwas_catalog-ancestry_r2019-10-23.tsv
* gwas_catalog_trait-mappings_r2019-10-23.tsv
* gwas_catalog_v1.0.2-associations_e94_r2019-10-23.tsv
* gwas_catalog_v1.0.2-studies_e94_r2019-10-23.tsv
* gwas_catalog_v1.0-associations_e94_r2019-10-23.tsv
* gwas_catalog_v1.0-studies_e94_r2019-10-23.tsv
* gwas-diagram.owl
* gwas-diagram.png
* gwas-diagram.svg
* gwas-kb.owl
* release_notes.txt

For the example readme see [attached file](README.txt) in the repo.
