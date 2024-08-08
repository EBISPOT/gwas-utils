import pandas as pd
import requests
import urllib.parse

class solrWrapper(object):

    def __init__(self, host, port, core, verbose = False):

        self.__host = host
        self.__port = port
        self.__core = core
        self.__verbose = verbose

        # Is the solr up?
        self.is_server_running()

        # Is there the requested core in the solr?
        self.is_core_OK()

        # Adding base URL:
        self.base_url = '{}:{}/solr/{}'.format(self.__host, self.__port, self.__core)
        self.clear_object()

    def clear_object(self):
        # Initialize internal values:
        self.docs = []
        self.facets = {}
        self.counts = 0

    def get_core_list(self):
        return(self.__cores)

    def get_core(self):
        return(self.__core)

    def get_host(self):
        return(self.__host)

    def get_port(self):
        return(self.__port)

    def is_core_OK(self):

        # Is the core is in the available cores:
        if self.__core not in self.__cores:
            print('[Error] Requested core ({}) is not in the supported cores: {}'.format(
                self.__core, ','.join(self.__cores)))
            return(1)

        # Generate URL:
        URL = '{}:{}/solr/{}/admin/ping?wt=json'.format(self.__host, self.__port, self.__core)
        content = self._submit(URL)
        
        # Is core OK?
        if content['status'] != 'OK':
            print('[Error] Core ({}) is down.'.format(self.__core))
            return(1)
        
        print('[Info] Core ({}) found.'.format(self.__core))

    def is_server_running(self):

        # Generate URL:
        URL = '{}:{}/solr/admin/cores?action=STATUS&wt=json'.format(self.__host, self.__port)
        content = self._submit(URL)
        
        # Parse cores:
        self.__cores = list(content['status'].keys())
        
        # Does it look good:
        print('[Info] Solr server ({}:{}/solr/) is up and running.'.format(self.__host, self.__port))
        
    def get_resource_counts(self,resouce):
        return(self.facets[resouce])
    
    def __len__(self):
        return len(self.docs)
    
    def get_study_table(self):
        resource_name = "study"

        # Field list retrieved from solr:
        fl_list = [
            "pubmedId",
            "title",
            "author_s",
            "accessionId",
            "fullPvalueSet",
            "associationCount",
            "catalogPublishDate",
            "publicationDate",
            "publication",
            "traitName_s",
            "mappedLabel",
            "mappedUri",
            "efoLink",
        ]

        self.get_facets()
        print("[Info] Facets fetched.")
        rows = self.get_resource_counts(resource_name)
        print(f"[Info] There are {rows} studies, querying them...")
        self.query(resourcename=resource_name, fl=fl_list, rows=rows)
        print("[Info] Query complete.")

        # Generate dataframe:
        return pd.DataFrame(self.docs)

    
    def reload_core(self):
        URL = '{}:{}/solr/admin/cores?action=RELOAD&core={}'.format(self.__host, self.__port, self.__core)
        content = self._submit(URL)
        return(1)

    def delete_query(self, query = None):
        '''
        This function deletes query from solr
        '''

        if query:
            doc_count = self.get_all_document_count()
            print('[Info] The following documents are deleted from solr: {}'.format(query))
            URL = '{}/update?commit=true'.format(self.base_url)

            content = self._submit(URL, jsonData = {"delete":{ "query" : query }})
            print('[Info] Number of documents in the {} core went from {} to {}'.format(self.__core, doc_count, self.get_all_document_count()))

        else:
            print('[Info] To delete documents from solr, please specify the query.')
        
        return(0)
        
    def wipe_core(self):
        print('[Info] Wiping all documents from {}...'.format(self.__core))
        self.delete_query("*:*")

    def add_document(self, documentFile):
        print("[Info] Adding {} to the solr core.".format(documentFile))
        URL = '{}/update?commit=true'.format(self.base_url)
        content = self._submit(URL, data = open(documentFile, 'rb'))
        return(0)

    def get_schema(self):
        URL = '{}/schema'.format(self.base_url)
        content = self._submit(URL)
        fieldsDf = pd.DataFrame(content['schema']['fields'])
        print('[Info] Schema retrieved. Number of fields: {}'.format(len(fieldsDf)))
        return(fieldsDf)

    def query(self, term = None, keyword_terms = None, rows = 100000, facet = None, fl = None, resourcename = None, wt='json'):
        
        # Let's build query URL:
        URL = '{}/select?'.format(self.base_url) 
        query = []
        
        # If there's a search term given:
        if term:
            query.append(term)
        
        # If there's keywords given:
        if keyword_terms:
            query += ['{}:{}'.format(key, value) for key, value in keyword_terms.items()]
        
        # If there's resourcename specified:
        if resourcename:
            query.append('resourcename:{}'.format(resourcename))
        
        # If something is given:
        if query:
            query_strig = ' AND '.join(query)
        else:
            query_strig = '*:*'
            
        # Start building the full request:
        fullRequest = {'q' : query_strig}
        
        # Is the output format specified:
        if wt:
            fullRequest['wt'] = wt
            
        # Is rows specified:
        fullRequest['rows'] = rows
            
        # Is facetting turned on:
        if facet:
            fullRequest['facet'] = 'true'
            fullRequest['facet.field'] = 'resourcename'
        
        # Are we restricting fields:
        if fl:
            fullRequest['fl'] = ','.join(fl)

        URL += urllib.parse.urlencode(fullRequest)
        
        # Submit query:
        result = self._submit(URL)
        
        # Save documents: 
        self.docs = result['response']['docs']
        
        # Save counts:
        self.counts = result['response']['numFound']
        
        # Save facet counts:
        if facet:
            resourcename = result['facet_counts']['facet_fields']['resourcename']
            self.facets = dict(zip(resourcename[::2],resourcename[1::2]))
            
        # Save URL:
        self.URL = URL
        
    def get_all_document_count(self):
        self.query(rows=1)
        return(self.counts)
        
    def get_facets(self):
        self.query(rows=1,facet=True)
        return(self.facets)
    
    def _submit(self, URL, headers={ "Content-Type" : "application/json", "Accept" : "application/json"}, jsonData = {}, data = ''):
        if not jsonData and not data:
            r = requests.get(URL, headers=headers, )
        elif data:
            r = requests.post(URL, headers=headers, data = data)
        else:
            r = requests.post(URL, headers=headers, json = jsonData)
        
        if not r.ok:
            r.raise_for_status()

        try:
            return(r.json())
        except:
            return(r.content)

