# Solr wrapper

This Python module makes it easy to query and namipulate the solr servers of the GWAS Catalog from Python. 

## Requirements

* [request](https://requests.kennethreitz.org/en/master/) : standard component of the Python core. Responsible to sending and 
receiving messages to/from the solr server.
* [pandas](https://pandas.pydata.org) : queries return data in pandas data frames.

## Installation

1. Clone repository
2. Activate the requrested Python environment
3. Install package:

```bash
cd solrWrapper
pip install .
```

## Usage

The package contains a single class. To initialize it needs the URL of the solr server, the port the server is listening, and the core name.

Upon initialization it's checked if the server is running and the core is present and available. If all good, the returned object can be used to query, get stats, reload the core; add new documents or wipe off.

#### Initialization


```python
from solrWrapper import solr_wrapper

host = 'http://localhost'
port = 8983
core = 'gwas'

solr = solr_wrapper(host, port, core)
```

Upon successful initialization, this should be written to the standard output:

```
[Info] Solr server (http://localhost:8983/solr/) is up and running.
[Info] Core (gwas) found.
```

#### Interfaces to retrieve data from solr

Health checks:

```python
solr.is_server_running() # Checks if server is up and running
solr.is_core_OK() # checks if the core is available
solr.get_core() # Get used core
solr.get_host() # get host name
solr.get_port() # get the used port
solr.get_core_list() # get a list of available cores on the solr server
```

Get facet counts (default facet field is `resourcename`):

```python
solr.get_facets()
```

Returns dictionary with resources as keys and their count as values:

```
{'association': 143963, 'study': 7100, 'diseasetrait': 4703, 'efotrait': 2610}
```

Get the number of all documents in the solr index:

```python
solr.get_all_document_count()
```

Get the schema of the given solr core in a pandas dataframe. The returned dataframe will contain all the field names, type, if the field is indexed, stored or multivalued:

```python
solr.get_schema()
```

Get document count for a particular resource (make sure that you run `solr.get_facets()` first):

```python
resource = 'study'
solr.get_resource_counts(resource)
```

Query the solr index - to get a pandas dataframe with all studies with the most frequently used fields.
Note that it returns exactly the number of studies returned by `solr.get_resource_counts('study')`

```python
study_df = solr.get_study_table()
```

There's a powerful, fully customizable method to submit queries to the solr index. User can 
define query term, keyword terms, requested resource name, list of returned fields, output format, number of output rows.

Example 1: return all studies reporting a given variant:

```python
solr.query(term = 'rs7329174', resourcename = 'study', fl = ['id', 'pubmedId', 'accessionId'])
len(solr) # Gives the number of results found
solr.docs # get the resulting documents
result_df = pd.DataFrame(solr.docs) # Format results to dataframe
```

#### Interfaces to update solr

Reload solr core:

```python
solr.reload()
```

Deleting objects from solr based on query:

```python
solr.delete_query('(resourcename:study OR resourcename:association) AND ( pubmedId:22683750 )')
```

Wiping out all documents from the core:

```python
solr.wipe_core()
```

Upload new documents:

```python
documentFile = 'testFolder/newDocs.json'
solr.addDocument(documentFile)
```

### More information

See confluence [page](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/Solr+wrapper).





