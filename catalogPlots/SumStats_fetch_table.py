import DBConnection
import argparse
import pandas as pd

getTableSQL = '''select T1.YEAR, T1.STUDY, T2.SS_STUDY, T1.PUBLICATION, T2.SS_PUBLICATION from
      (
        SELECT to_char(P.PUBLICATION_DATE, 'YYYY') as YEAR,
          count(S.ID) as STUDY,
          count(distinct(P.ID)) as PUBLICATION
        FROM STUDY S,
          HOUSEKEEPING HK,
          PUBLICATION P
        WHERE S.HOUSEKEEPING_ID = HK.ID
          AND HK.IS_PUBLISHED = 1
          AND S.PUBLICATION_ID = P.ID
        GROUP BY to_char(P.PUBLICATION_DATE, 'YYYY')
        ORDER BY to_char(P.PUBLICATION_DATE, 'YYYY') ASC
      ) T1
    LEFT JOIN
      (
        SELECT to_char(P.PUBLICATION_DATE, 'YYYY') as YEAR,
          count(S.ID) as SS_STUDY,
          count(distinct(P.ID)) as SS_PUBLICATION
        FROM STUDY S,
          HOUSEKEEPING HK,
          PUBLICATION P
        WHERE S.HOUSEKEEPING_ID = HK.ID
          AND HK.IS_PUBLISHED = 1
          AND S.PUBLICATION_ID = P.ID
          AND S.FULL_PVALUE_SET = 1
        GROUP BY to_char(P.PUBLICATION_DATE, 'YYYY')
        ORDER BY to_char(P.PUBLICATION_DATE, 'YYYY') ASC
      ) T2
    ON T1.YEAR = T2.YEAR'''


def main():
    # Parsing command line arguments:
    parser = argparse.ArgumentParser(description='This script fetches the yearly count of studies and publication with and without summary stats.')
    parser.add_argument('--filename', type = str, required=True, help = 'Output filename.')

    args = parser.parse_args()
    filename = args.filename

    # Fetch table from database:
    dbObject = DBConnection.gwasCatalogDbConnector('spotpro')
    df = pd.read_sql(getTableSQL, dbObject.connection)

    # Update column names:
    df.columns = ["year", "studies", "studiesSS", "publication", "publicationSS"]

    # Save table:
    df.to_csv(filename, index=None, na_rep=0)


if __name__ == '__main__':
    main()
