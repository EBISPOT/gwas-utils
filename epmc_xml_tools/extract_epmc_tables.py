### Extracts tables and associated titles, legends etc. from ePMC full-text XML

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

### Functions ###

def get_pmcid(pmid):
    '''Calls the NCBI ID Converter API to convert PMID to PMCID'''
    url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=' + pmid + '&format=json&tool=notyetnamed&email=eks@ebi.ac.uk'
    response = requests.get(url)
    # parse the JSON
    a = response.json()
    # return the pmcid from the JSON response
    pmcid = a['records'][0]['pmcid']
    return pmcid
    
def get_xml(pmcid):
    '''Calls the Europe PMC API with a PMCID and returns the raw XML for the article'''
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/' + pmcid + '/fullTextXML'
    response = requests.get(url)
    return response.content

def make_soup(xml):
    '''Given raw XML, returns parsed XML as a beautiful soup object'''
    return bs(xml, 'lxml')

def format_soup(soup):
    '''Converts a beautiful soup object to a string with more readable formatting'''
    return soup.prettify()

def write_xmlfile(xmlstring):
    '''Writes a formatted XML string to an XML file for reference'''
    filename = pmid + '.xml'
    with open(filename, 'w') as xmlfile:
        xmlfile.write(xmlstring)

def get_tables(xml):
    '''Returns a list of html tables from an XML file'''
    return pd.read_html(xml)

def write_to_excel(tables):
    '''Iterates over tables in a list and writes to excel'''
    n = 1
    for table in tables:
        # write to file then increase filename increment
        filename = pmid + '_table_' + str(n) + '.xlsx'
        print('Writing to file', filename)
        table.to_excel(filename)
        n += 1

def get_table_summaries(soup):
    '''Extracts table numbers, titles & legends from beautiful soup object'''
    # filter soup to select only <div class="table-wrap..."> tags
    table_soup = soup.find_all("table-wrap")
    # create empty string to store table details
    summaries = ''
    for wrap in table_soup:
        # extract table number from <label> tag (text only)
        number = wrap.label.get_text()
        # extract table title from <caption> tag (text only)
        title = wrap.caption.get_text()
        # extract table legend from <table-wrap-foot> tag (text only)
        try:
            legend = wrap.find("table-wrap-foot").get_text()
        except:
            legend = '<no legend>'
        # append table details to string
        summaries += number + '\nTitle: ' + title + '\nLegend: ' + legend + '\n\n'
    return summaries

def write_outline(summaries):
    filename = pmid + '_outline.txt'
    with open(filename, 'w') as outline:
        outline.write(summaries)

### Run ###

# try to get PMCID from PMID
pmid = input('Enter PMID: ')
try:
    pmcid = get_pmcid(pmid)
    print('Found PMCID:', pmcid)
# if no PMCID found, print error message and quit
except:
    print('No PMCID found for this PMID. Full text may not be available.')
    quit()

# get the xml file from ePMC
#pmcid = input('Enter PMCID: ')
xml = get_xml(pmcid)
print('Retrieved raw XML.')

# write xml to file to keep as a reference
soup = make_soup(xml)
xmlstring = format_soup(soup)
write_xmlfile(xmlstring)
print('XML written to file.')

# get the list of tables
tables = get_tables(xml)
print('Extracted', len(tables), 'tables.')
# write each table to excel
write_to_excel(tables)
print('Tables written to excel.')

# get the summary text
summaries = get_table_summaries(soup)
print('Extracted table summaries:', len(summaries), 'characters.')
# write to report
write_outline(summaries)
print('Table outline written to txt.')