### Extracts tables and associated titles, legends etc. from ePMC full-text XML

import requests
import pandas as pd
import argparse
import sys
from bs4 import BeautifulSoup as bs


class EPMCClient:
    def __init__(self, pmid):
        self.pmid = pmid
        self.pmcid = None
        self.base_url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'

    def get_pmcid(self):
        '''Calls Europe PMC API with a PMID and retrieves the matching PMCID'''
        url = self.base_url + 'search?query=SRC%3AMED%20AND%20EXT_ID%3A' + self.pmid + '&resultType=idlist&cursorMark=*&pageSize=25&format=json'
        try:
            response = requests.get(url)
            if response.content:
                a = response.json()
                try:
                    pmcid = a['resultList']['result'][0]['pmcid']
                    return pmcid
                except:
                    print("No pmcid found for pmid: {}".format(self.pmid))
                    sys.exit()
            else:
                print("pmid: {} not found".format(self.pmid))
                sys.exit()
        except requests.exceptions.ConnectionError as e:
            print(e)
            sys.exit()

    def set_pmcid(self):
        self.pmcid = self.get_pmcid()

    def get_xml(self):
        '''Calls the Europe PMC API with a PMCID and returns the raw XML for the article'''
        url = self.base_url + self.pmcid + '/fullTextXML'
        try:
            response = requests.get(url)
            if response.content:
                return response.content
            else:
                print("No content for pmid: {}".format(self.pmid))
                sys.exit()
        except requests.exceptions.ConnectionError as e:
            print(e)
            sys.exit()

    @staticmethod
    def format_soup(soup):
        '''Converts a beautiful soup object to a string with more readable formatting'''
        return soup.prettify()

    def write_xmlfile(self, xmlstring):
        '''Writes a formatted XML string to an XML file for reference'''
        filename = self.pmid + '.xml'
        with open(filename, 'w') as xmlfile:
            xmlfile.write(xmlstring)

    @staticmethod
    def get_tables(xml):
        '''Returns a list of html tables from an XML file'''
        try:
            return pd.read_html(xml)
        except ValueError as e:
            print(e)
            sys.exit()

    def write_to_excel(self, tables):
        '''Iterates over tables in a list and writes to excel'''
        n = 1
        for table in tables:
            # write to file then increase filename increment
            filename = self.pmid + '_table_' + str(n) + '.xlsx'
            print('Writing to file', filename)
            table.to_excel(filename)
            n += 1

    @staticmethod
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
            table_wrap_foot = wrap.find("table-wrap-foot")
            legend = table_wrap_foot.get_text() if table_wrap_foot else '<no legend>'
            # append table details to string
            summaries += number + '\nTitle: ' + title + '\nLegend: ' + legend + '\n\n'
        return summaries

    def write_outline(self, summaries):
        filename = self.pmid + '_outline.txt'
        with open(filename, 'w') as outline:
            outline.write(summaries)

    @staticmethod
    def make_soup(xml):
        '''Given raw XML, returns parsed XML as a beautiful soup object'''
        return bs(xml, 'lxml')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pmid', type=str, help='PMID', default=None, required=False)
    args = parser.parse_args()
    pmid = args.pmid if args.pmid else input('Enter PMID: ')

    epmc_client = EPMCClient(pmid=pmid)

    # set pmcid for given pmid
    epmc_client.set_pmcid()
    print('Set PMCID:', epmc_client.pmcid)
    
    # get the xml file from ePMC
    xml = epmc_client.get_xml()
    print('Retrieved raw XML.')

    # write xml to file to keep as a reference
    soup = epmc_client.make_soup(xml)
    xmlstring = epmc_client.format_soup(soup)
    epmc_client.write_xmlfile(xmlstring)
    print('XML written to file.')

    # get the list of tables
    tables = epmc_client.get_tables(xml)
    print('Extracted', len(tables), 'tables.')
    # write each table to excel
    epmc_client.write_to_excel(tables)
    print('Tables written to excel.')

    # get the summary text
    summaries = epmc_client.get_table_summaries(soup)
    print('Extracted table summaries:', len(summaries), 'characters.')
    # write to report
    epmc_client.write_outline(summaries)
    print('Table outline written to txt.')


if __name__ == '__main__':
    main()
