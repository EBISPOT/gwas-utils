import pandas as pd
from gwas_db_connect import DBConnection


def get_db_updates(old_table, new_table):
    '''
    This function returns dictionary with lists of pmids of studies removed/added/updated.
    '''

    # This is the list of pubmedID that will be updated:
    pmid_changes = {
        "added" : [],
        "removed" : [],
        "updated" : []
    }

    # Determine newly added studies:
    new_studies = new_table.loc[new_table.index.difference(old_table.index, sort=None)]
    if len(new_studies) == 0:
        print('\n[Info] No new study has been added since the last data release')
    else:
        print('\n[Info] {} studies from {} publications were newly added:'.format(len(new_studies), len(new_studies.PUBMED_ID.unique())))
        new_studies.apply(lambda row: print("\t{}, PMID: {}, catalog added date: {}".format(
            row['ACCESSION_ID'], row['PUBMED_ID'], row['CATALOG_PUBLISH_DATE'])), axis = 1)
        pmid_changes['added'] += new_studies.PUBMED_ID.unique().tolist()

    # Determine retracted studies:
    retracted_studies = old_table.loc[old_table.index.difference(new_table.index, sort=None)]
    if len(retracted_studies) == 0:
        print('\n[Info] No study has been retracted since the last data release')
    else:
        print('\n[Info] {} studies from {} publications were retraced:'.format(len(retracted_studies), len(retracted_studies.PUBMED_ID.unique())))
        retracted_studies.apply(lambda row: print("\t{}, PMID: {}, catalog added date: {}".format(
            row['ACCESSION_ID'], row['PUBMED_ID'], row['CATALOG_PUBLISH_DATE'])), axis = 1)
        pmid_changes['removed'] += retracted_studies.PUBMED_ID.unique().tolist()

    # Determine updated studies:
    merged = new_table.merge(old_table, how='outer', suffixes=('_x', '_y'))
    updated = merged.loc[merged.ACCESSION_ID.duplicated()]
    if len(updated) == 0:
        print('\n[Info] No study has been updated since the last data release')
    else:
        print('\n[Info] {} studies were updated from {} publications.'.format(len(updated), len(updated.PUBMED_ID.unique())))
        updated.ACCESSION_ID.apply(lambda x: print("\t{} new date: {:%Y %b %d} vs. old date: {:%Y %b %d}".format(x, new_table.loc[x].LAST_UPDATE_DATE, old_table.loc[x].LAST_UPDATE_DATE)))
        pmid_changes['updated'] += updated.PUBMED_ID.unique().tolist()

    return(pmid_changes)

def get_studies(instance):
    '''
    Given the database instance, this function returns with the published studies
    '''
    
    study_table_sql = '''SELECT
          S.ID as STUDY_ID,
          S.ACCESSION_ID,
          P.PUBMED_ID,
          HK.LAST_UPDATE_DATE,
          HK.CATALOG_PUBLISH_DATE
        FROM
          STUDY S,
          PUBLICATION P,
          HOUSEKEEPING HK
        WHERE HK.ID = S.HOUSEKEEPING_ID
          AND S.PUBLICATION_ID = P.ID
          AND HK.IS_PUBLISHED = '1'
    '''
    
    connection = DBConnection.gwasCatalogDbConnector(instance)
    study_table = pd.read_sql(study_table_sql, connection.connection)
    study_table.index = study_table.ACCESSION_ID.tolist()
    
    connection.close()
    return study_table


