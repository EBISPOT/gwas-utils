import pandas as pd
import requests
from datetime import datetime


class getDataFromSolr(object):
    def __init__(self, solrAddress, core, verbose = False):
        self.__core__ = core
        self.__verbose__ = verbose
        self.__address__ = solrAddress
        self.__URL__ = 'http://%s/solr/%s' % (solrAddress, core)

        print('[INFO] Extracting data from: %s' % solrAddress)
        
    def getStudies(self):
        URL = self.__URL__ + '/select?q=resourcename:study&wt=json&indent=true&fl=pubmedId,id,accessionId,title,associationCount&from=0&rows=10000'
        response = self.__submitRequest__(URL)
        data = response['response']['docs']
        return(pd.DataFrame(data))

    def getLastStudy(self):
        URL = self.__URL__ + '/select?q=resourcename%3Astudy+&sort=catalogPublishDate+desc&rows=1&fl=catalogPublishDate&wt=json&indent=true'
        response = self.__submitRequest__(URL)
        lastDate = response['response']['docs'][0]['catalogPublishDate']
        # date = datetime.strptime(lastDate, '%Y-%m-%dT%H:%M:%SZ')
        return(lastDate)

    def getNewStudies(self, lastDate):
        URL = self.__URL__ + ('/select?q=resourcename%%3Astudy+AND+catalogPublishDate%%3A%%5B%s+TO+*%%5D&rows=10000&&fl=pubmedId,id,accessionId,title,associationCount&wt=json&indent=true' % lastDate)
        response = self.__submitRequest__(URL)
        data = response['response']['docs']
        return(pd.DataFrame(data))

    def getAssociationCount(self):
        URL = self.__URL__ + '/select?q=resourcename%3Aassociation&rows=1&fl=id&wt=json&indent=true'
        response = self.__submitRequest__(URL)
        associationCnt = response['response']['numFound']
        return(associationCnt)
    
    def __submitRequest__(self, URL):
        r = requests.get(URL)
        if self.__verbose__: print(URL)
        if r.status_code == 200:
            return (r.json())
        else:
            print("[Warning] The requested URL (%s) failed to retrieve." % URL)
            return ({"response": "Request failed.", "responseCode" : r.status_code, "resopnse" : r.content })

