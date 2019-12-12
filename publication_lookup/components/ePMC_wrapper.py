import requests
from collections import OrderedDict
from urllib.parse import quote
import re
import pandas as pd


# This is a wrapper object to fetch data from the Euro PMC REST API.
# The URL and a handful of other features are hardcoded. Not particularly flexible, but works.

class ePMC_wrapper():
    
    # The following variables are used to build a query:
    email = 'gwas-info@ebi.ac.uk'
    URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
    retType = 'json'
    resultType = 'lite'
    verbose = False

    # Initializing publication container:
    _publications = []

    # Email extraction;
    EMAIL_REGEX = re.compile(r"\S+\@.+\.")
    
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

        self._publications = []
        
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

        # Report Error:
        if 'error' in data:
            print(data['error'])
            print(data['content'])
            print(requestURL)

        # If the resultset is empty, just return empty array:
        try:
            if data['hitCount'] == 0:
                if self.verbose: print('[Warning] No hit found for: {}'.format(requestURL))
                return None

        except TypeError as e:
            print('Type error: {}'.format(requestURL))
            return None

        self._publications = data['resultList']['result'] 
        return None

    def parse_field(self):

        def _parser(row):
            return_data = OrderedDict()
            
            # Extract pmid:
            return_data['pmid'] = row['pmid'] if 'pmid' in row else None

            # Extract title:
            return_data['title'] = row['title'] if 'title' in row else None

            # Extract pmid:
            return_data['authors'] = row['authorString'] if 'authorString' in row else None

            # Extract title:
            return_data['date'] = row['firstPublicationDate'] if 'firstPublicationDate' in row else None

            # Extract journal:
            if 'journalTitle' in row:
                return_data['journal'] = row['journalTitle']
            elif 'journalInfo' in row:
                return_data['journal'] = row['journalInfo']['journal']['title']
            else:
                return_data['journal'] = None

            # Extract email:
            c_author = []
            c_emails = []
            c_orcid  = []
            if 'authorList' in row:
                for author in row['authorList']['author']:
                    if 'affiliation' not in author: continue

                    email = self.EMAIL_REGEX.findall(author['affiliation'])
                    
                    if len(email) > 0:
                        c_emails += email
                        c_author.append(author['fullName'])
                        if 'authorId' in author and 'type' in author['authorId']:
                            c_orcid.append(author['authorId']['value'])
            
            return_data.update({
                'c_author': ','.join(list(set(c_author))),
                'c_email' : ','.join(list(set(c_emails))),
                'c_orcid' : ','.join(list(set(c_orcid)))
            })

            return return_data

        # These are the extractable fields. Feel free to further extend:
        field_list = ['pmid','title','authors','date','date','journal','email']

        returnData = []

        # Returning empty dataframe if there's no publication:
        if len(self._publications) == 0: 
            return pd.DataFrame([{x : None for x in field_list}])

        # Parse fields from each publications:
        for article in self._publications:
            returnData.append(_parser(article))

        return pd.DataFrame(returnData)


    def __getURL(self, URL):
        r = requests.get(URL)
        
        if not r.ok:
            return(['[Error] Request failed for {}.\n[Error] code: {}.\n[Error] content: {}'.format(URL, r.status_code, r.text)])
        
        try:
            
            return(r.json())
        except:
            return({'error': '[Error] The returned data is not JSON', 'content' : r.content})

