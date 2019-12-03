import requests
from urllib.parse import quote

# This is a wrapper object to fetch data from the Euro PMC REST API.
# The URL and a handful of other features are hardcoded. Not particularly flexible, but works.

class ePMC_wrapper():
    
    # The following variables are used to build a query:
    email = 'gwas-info@ebi.ac.uk'
    URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
    retType = 'json'
    resultType = 'lite'
    verbose = False
    
    def __init__(self, retType = None, resultType = None, email = None, verbose = None):
        
        # If provided with the init, update parameters:
        if retType:
            self.retType = retType
        
        if resultType:
            self.resultType = resultType
            
        if email:
            self.email = email
            
        if verbose:
            self.verbose = verbose
        
        return None
    
    def _clearSurname(self, authorString):
        surname = authorString.split(',')[0]
        cleanSurname = self._clearAuthor(surname)
        return(cleanSurname)
    
    def _clearAuthor(self, authorString):
        cleanAuthor = authorString.replace(',', ' ')
        cleanAuthor = cleanAuthor.replace('.', '')
        return(cleanAuthor)
    
    def _clearText(self, text):
        cleanText = text.replace('(','')
        cleanText = cleanText.replace(')','')
        cleanText = cleanText.replace('/', ' ')
        cleanText = cleanText.replace('=', ' ')
        return(cleanText)
        
    def search(self, queryTerms):
        
        # Building query string:
        queryStrings = []
        
        # Search by PMID:
        if 'pmid' in queryTerms:
            queryStrings = ['EXT_ID:{}'.format(queryTerms['pmid'])]
        
        # Searching with surname only:
        if 'surname' in queryTerms:
            cleanAuthor = self._clearSurname(queryTerms['surname'])
            queryStrings.append('author:"{}" '.format(cleanAuthor))
        
        # If the query term has author:
        if 'author' in queryTerms:
            cleanAuthor = self._clearAuthor(queryTerms['author'])
            queryStrings.append('author:"{}" '.format(cleanAuthor))
        
        # If query terms has title:
        if 'title' in queryTerms:
            cleanTitle = self._clearText(queryTerms['title'])
            queryStrings.append('title:"{}"'.format(cleanTitle))
            
        # If query term is no specified:
        if 'others' in queryTerms:
            cleanString = self._clearText(queryTerms['others'].replace(':',''))
            queryStrings.append(cleanString)

        # If query term is no specified:
        if 'fuzzyTitle' in queryTerms:
            cleanTitle = self._clearText(queryTerms['fuzzyTitle'])
            queryStrings.append('title: {} '.format(cleanTitle))            
        
        queryString = ' AND '.join(queryStrings)
        queryString = quote(queryString, '')
    
        # Building query:
        requestURL = '{url}/query={searchTerm}&resultType={resultType}&email={email}&format={retmode}'.format(**{
            'url': self.URL,
            'searchTerm' : queryString,
            'email' : self.email,
            'retmode' : self.retType,
            'resultType' : self.resultType
        })
        
        if self.verbose: print(requestURL)

        # Fetch data:
        data = self.__getURL(requestURL)
        returnData = []
        
        # Report Error:
        if 'error' in data:
            print(data['error'])
            print(data['content'])
            print(requestURL)
            return([])
        
        # If the resultset is empty, just return empty array:
        try:
            if data['hitCount'] == 0:
                if self.verbose: print('[Warning] No hit found for: {}'.format(requestURL))
                return(returnData)

        except TypeError as e:
            print('Type error: {}'.format(requestURL))
            
        # Looping through all resuls and parsing out relevant info:
        for result in data['resultList']['result']:

            try:
                returnData.append({'pmid' : result['pmid'],
                                'title'   : result['title'],
                                'authors' : result['authorString'],
                                'date'    : result['firstPublicationDate'],
                                'journal' : result['journalTitle']})

            except KeyError as e:
                continue
                
        return(returnData)
    
    def __getURL(self, URL):
        r = requests.get(URL)
        
        if not r.ok:
            return(['[Error] Request failed for {}.\n[Error] code: {}.\n[Error] content: {}'.format(URL, r.status_code, r.text)])
        
        try:
            
            return(r.json())
        except:
            return({'error': '[Error] The returned data is not JSON', 'content' : r.content})

