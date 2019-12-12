# Publication lookup

This script was written for efficiently looking up publications in the GWAS Catalog database. The input data is a txt file containing Pubmed IDs listed in a single column. The output is a tsv file with the following columns: 
* pubmed_id
* title
* publication_date
* journal
* first_author
* c_author
* c_email
* c_orcid
* in_catalog
* study_accession
* summary_stats

## Requirements

Written for `Python 3.6`

Custom Python packages:

 * `gwas_db_connect` : this package help connecting to database instances of the GWAS Catalog [link](https://gitlab.ebi.ac.uk/gwas/gwas_db_connect/commits/master)

## Usage

```bash
python ${scriptDir}/publication_lookup.py \
    --dbInstance ${dbInstance} \
    --input ${input_filename} \
    --output ${output_filename}
```

**Where**:

* `dbInstance` is the database instance name from which the publications are looked up.
* `input` txt file where each line contains one title or pmid
* `output` the filename into which the table is saved in tsv format. Default value: `output.tsv`

## Corresponding author info

The corresponding author information is not indexed by EuroPMC (see API [documentation](https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf)) but it might be included in the author field or the affiliation field. It has to be parsed out. Look for `@` sign. 

See an example [here](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=ext_id:31657339&resultType=core&format=json):

```json
"authorList": {
    "author": [
        {
            "fullName": "Ma Y",
            "firstName": "Yue",
            "lastName": "Ma",
            "initials": "Y",
            "affiliation": "Department of Cardiology, Tianjin Chest Hospital, Tianjin 300222, China. Corresponding author: Zhang Jingxia, Email: zhangjingxia001@126.com."
        }
    ]
},
"affiliation": "Department of Cardiology, Tianjin Chest Hospital, Tianjin 300222, China. Corresponding author: Zhang Jingxia, Email: zhangjingxia001@126.com.",
```