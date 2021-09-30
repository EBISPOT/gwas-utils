import requests
import urllib
import logging
import pandas as pd


logging.basicConfig(level=logging.DEBUG, format='(%(levelname)s): %(message)s')
logger = logging.getLogger(__name__)


# Constants
GWAS_STUDY_DOWNLOAD_URL = "https://www.ebi.ac.uk/gwas/api/search/downloads/studies_alternative"
GWAS_API_BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"


def fetch_gwas_study_table():
    logger.info("Fetchng study table download from: {}".format(GWAS_STUDY_DOWNLOAD_URL))
    gwas_study_df = pd.read_table(GWAS_STUDY_DOWNLOAD_URL)
    return gwas_study_df

def fetch_sumstats_status():
    logger.info("Fetchng study sumstats status from GWAS API")
    study_sumstats_dict = {}
    api_params = {"size": 1000}
    request_url = GWAS_API_BASE_URL + "/studies?" + urllib.parse.urlencode(api_params)
    logger.debug(request_url)
    api_response = requests.get(request_url).json()
    log_page_info(api_response)
    study_sumstats_dict.update(parse_api_response(api_response))
    while "next" in api_response["_links"]:
        api_response = requests.get(api_response["_links"]["next"]["href"]).json()
        log_page_info(api_response) 
        study_sumstats_dict.update(parse_api_response(api_response))
    sumstats_status_df = pd.DataFrame(study_sumstats_dict.items(), 
                                      columns=['study_accession', 'has_sumstats']
                                      )
    return sumstats_status_df

def parse_api_response(api_response):
    study_sumstats_dict = {}
    for study in api_response["_embedded"]["studies"]:
        study_sumstats_dict[study["accessionId"]] = study["fullPvalueSet"]
    return study_sumstats_dict

def log_page_info(api_response):
    return logger.info("Page {} of {}".format(
                        api_response["page"]["number"], 
                        api_response["page"]["totalPages"])
                        )

def merge_sumstats_status_with_study_table(gwas_study_df, sumstats_status_df):
    logger.info("Merging study download table with sumstats statuses")
    merged_df = pd.merge(gwas_study_df, 
                         sumstats_status_df, 
                         how="left", 
                         left_on="STUDY ACCESSION", 
                         right_on="study_accession"
                         ).drop(columns='study_accession')
    return merged_df


def write_df_to_file(dataframe, filename):
    logger.info("Writing table data to {}".format(filename))
    dataframe.to_csv(filename, sep="\t", index=False, na_rep="NA")

def main():
    sumstats_status_df = fetch_sumstats_status()
    gwas_study_df = fetch_gwas_study_table()
    merged_df = merge_sumstats_status_with_study_table(gwas_study_df, sumstats_status_df)
    write_df_to_file(merged_df, "study_download_with_sumstats_status.tsv")


if __name__ == '__main__':
    main()
