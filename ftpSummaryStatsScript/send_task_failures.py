import smtplib
from datetime import datetime, time, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pymongo import MongoClient


def fetch_failures_yesterday():
    # MongoDB setup
    uri = ""
    client = MongoClient(uri)
    db = client["gwasdepo"]
    collection = db["sumstats-celery-task-failures"]

    # Date range for yesterday
    end_date = datetime.combine(datetime.today().date(), time(22, 0))
    start_date = end_date - timedelta(hours=24)

    # Query to fetch failures from yesterday
    query = {"timestamp": {"$gte": start_date, "$lt": end_date}}
    failures = collection.find(query)

    return list(failures), start_date, end_date


def format_failures(failures):
    failure_messages = []
    for failure in failures:
        gcst_id = failure["gcst_id"]
        exception = failure["exception"]
        timestamp = failure["timestamp"]
        message = f"{timestamp} - {gcst_id} - {exception}"
        failure_messages.append(message)

    return "\n".join(failure_messages)


def send_email(failure_report, start_date, end_date):
    # Email setup
    server = "localhost"
    subject = f"Metadata YAML generation failures between {start_date} and {end_date}"

    # Construct email
    msg = MIMEMultipart()
    msg["From"] = "gwas-dev@ebi.ac.uk"
    msg["To"] = "gwas-dev@ebi.ac.uk"
    msg["Subject"] = subject
    body = f"The following GCSTs failed for metadata YAML generation:\n\n{failure_report}"  # noqa: E501
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(server) as server:
        server.send_message(msg)


if __name__ == "__main__":
    failures, start_date, end_date = fetch_failures_yesterday()
    if failures:
        failure_report = format_failures(failures)
        send_email(failure_report, start_date, end_date)
    else:
        print("No failures found for yesterday.")
