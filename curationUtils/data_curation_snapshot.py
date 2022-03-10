import argparse
import csv
import datetime
from gwas_db_connect import DBConnection
import smtplib
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def get_data_curation_snapshot(database_name):
    '''
    Get data curation snapshot. This is a modified version of the query used to
    create the data in the MONTHLY_TOTALS_SUMMARY_VIEW, which is displayed on
    the "Monthly Curator Totals" Report page.
    '''
    db_handler = DBConnection.gwasCatalogDbConnector(database_name)
    cursor = db_handler.cursor

    sql_data_curation_snapshot = """
        SELECT PUBMED_ID, CURATION_STATUS, CURATOR_TOTAL
        FROM MONTHLY_TOTALS_SUMMARY_VIEW
        WHERE YEAR >= 2016
    """

    cursor.execute(sql_data_curation_snapshot)
    data = cursor.fetchall()
    db_handler.close()
    return data


def generate_data_report(data, report_filename):
    '''
    Process data into curation bins and count number of
    the number of publications and studies in each bin.
    '''

    level_1_pubs = 0
    level_1_studies = 0
    level_1_pubs_seen = []

    level_2_pubs = 0
    level_2_studies = 0
    level_2_pubs_seen = []

    awaiting_literature_pubs = 0
    awaiting_literature_studies = 0
    awaiting_literature_pubs_seen = []

    awaiting_efo_pubs = 0
    awaiting_efo_studies = 0
    awaiting_efo_pubs_seen = []

    awaiting_mapping_pubs = 0
    awaiting_mapping_studies = 0
    awaiting_mapping_pubs_seen = []

    outstanding_query_pubs = 0
    outstanding_query_studies = 0
    outstanding_query_pubs_seen = []

    fully_curated_yet_to_be_published_pubs = 0
    fully_curated_yet_to_be_published_studies = 0
    fully_curated_yet_to_be_published_pubs_seen = []

    published_pubs = 0
    published_studies = 0
    published_pubs_seen = []

    # Break down into bins
    for row in data:
        pubmed_id = row[0]
        curation_status = str(row[1]).lower()
        study_count = int(row[2])

        # Count Level 1
        if curation_status in ["awaiting curation", "awaiting literature", \
            "preliminary review done", "level 1 ancestry done"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in level_1_pubs_seen:
                level_1_pubs += 1
                level_1_pubs_seen.append(pubmed_id)

            level_1_studies += study_count


        # Count Level 2
        if curation_status in ["level 1 curation done", "level 2 ancestry done"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in level_2_pubs_seen:
                level_2_pubs += 1
                level_2_pubs_seen.append(pubmed_id)

            level_2_studies += study_count


        # Awaiting Literature
        if curation_status in ["awaiting literature"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in awaiting_literature_pubs_seen:
                awaiting_literature_pubs += 1
                awaiting_literature_pubs_seen.append(pubmed_id)

            awaiting_literature_studies += study_count


        # Awaiting EFO
        if curation_status in ["awaiting efo assignment"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in awaiting_efo_pubs_seen:
                awaiting_efo_pubs += 1
                awaiting_efo_pubs_seen.append(pubmed_id)

            awaiting_efo_studies += study_count


        # Awaiting Mapping
        if curation_status in ["awaiting mapping"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in awaiting_mapping_pubs_seen:
                awaiting_mapping_pubs += 1
                awaiting_mapping_pubs_seen.append(pubmed_id)

            awaiting_mapping_studies += study_count


        # Outstanding query
        if curation_status in ["outstanding query"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in outstanding_query_pubs_seen:
                outstanding_query_pubs += 1
                outstanding_query_pubs_seen.append(pubmed_id)

            outstanding_query_studies += study_count


        # Fully curated, yet to be published
        if curation_status in ["level 2 curation done", "awaiting mapping", "awaiting efo assignment"]:
        # if curation_status in ["level 2 curation done"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in fully_curated_yet_to_be_published_pubs_seen:
                fully_curated_yet_to_be_published_pubs += 1
                fully_curated_yet_to_be_published_pubs_seen.append(pubmed_id)

            fully_curated_yet_to_be_published_studies += study_count


        # Published
        if curation_status in ["publish study", "requires re-curation"]:
            # Add pubmed_id to list of PubmedIDs seen in this catagory
            if pubmed_id not in published_pubs_seen:
                published_pubs += 1
                published_pubs_seen.append(pubmed_id)

            published_studies += study_count

    # Today's date
    now = datetime.datetime.now()
    datestamp = str(now.day)+"_"+str(now.year)+"_"+str(now.month)


    # Prepare report file
    with open(report_filename, 'a') as output_file:
        csvout = csv.writer(output_file)

        csvout.writerow([datestamp, level_1_pubs, level_1_studies, \
            level_2_pubs, level_2_studies, awaiting_literature_pubs, awaiting_literature_studies, \
            awaiting_efo_pubs, awaiting_efo_studies, awaiting_mapping_pubs, awaiting_mapping_studies, \
            outstanding_query_pubs, outstanding_query_studies, fully_curated_yet_to_be_published_pubs, \
            fully_curated_yet_to_be_published_studies, published_pubs, published_studies])


def sendEmailReport(report_filename, emailFrom, emailTo):
    now = datetime.datetime.now()
    datestamp = str(now.day) + "_" + str(now.strftime("%b")) + "_" + str(now.year)
    try:
        with open(report_filename, 'r') as f:
            attachment = MIMEApplication(f.read(), Name=basename(report_filename))
            msg = MIMEMultipart()
            attachment['Content-Disposition'] = 'attachment; filename="%s"' % basename(report_filename)
            msg.attach(attachment)
            msg['Subject'] = 'GWAS Weekly Queue Snapshot '+datestamp
            msg['From'] = emailFrom
            msg['To'] = emailTo
            s = smtplib.SMTP('localhost')
            s.sendmail(emailFrom, emailTo, msg.as_string())
            s.quit()
    except OSError as e:
        print(e)


def main():
    '''
    Create snapshot of data curation progress.
    '''

    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', default='spotpro', choices=['dev3', 'spotpro'],
                        help='Database to use')
    parser.add_argument('--mode', default='debug', choices=['debug', 'production'],
                        help='Run as (default: debug).')
    parser.add_argument('--emailRecipient', type=str, help='Email address where the notification is sent.')
    parser.add_argument('--emailFrom', type=str, help='Email address where the notification is from.')
    parser.add_argument('--outfile', type=str, help='Name of the report filename', default='curation_snapshot_queue.csv')

    args = parser.parse_args()
    database = args.database
    sender = args.emailFrom
    recipient = args.emailRecipient
    report_filename = args.outfile

    # Run query to get data
    curation_progress_data = get_data_curation_snapshot(database_name=database)

    # Process data
    generate_data_report(data=curation_progress_data, report_filename=report_filename)

    # Email data to curators
    send_email(report_filename, sender, recipient)


if __name__ == '__main__':
    main()

