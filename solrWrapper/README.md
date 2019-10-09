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
from solrWrapper import solrWrapper

host = 'http://localhost'
port = 8983
core = 'gwas'

solr = solrWrapper(host, port, core)
```

Upon successful initialization, this should be written to the standard output:

```
[Info] Solr server (http://localhost:8983/solr/) is up and running.
[Info] Core (gwas) found.
```

#### Interfaces to retrieve data from solr

Health checks:

```python
solr.isServerRunning() # Checks if server is up and running
solr.isCoreOK() # checks if the core is available
solr.get_core() # Get used core
solr.get_host() # get host name
solr.get_port() # get the used port
solr.get_core_list() # get a list of available cores on the solr server
```

Get facet counts (default facet field is `resourcename`):

```python
solr.getFacets()
```

Returns dictionary with resources as keys and their count as values:

```
{'association': 143963, 'study': 7100, 'diseasetrait': 4703, 'efotrait': 2610}
```

Get the number of all documents in the solr index:

```python
solr.getAllDocumentCount()
```

Get the schema of the given solr core in a pandas dataframe. The returned dataframe will contain all the field names, type, if the field is indexed, stored or multivalued:

```python
solr.getSchema()
```

Get document count for a particular resource:

```python
resource = 'study'
solr.getResourceCounts(resource)3
```

Query the solr index - to get a pandas dataframe with all (<100k) studies with the most frequently used fields.

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

Wiping out all documents from the core:

```python
solr.wipeCore()
```

Upload new documents:

```python
documentFile = 'testFolder/newDocs.json'
solr.addDocument(documentFile)
```





