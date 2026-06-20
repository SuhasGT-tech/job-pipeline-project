"""
Sends daily email digests of job postings first seen TODAY (i.e. genuinely
new since the last run, not postings already known from a previous day).

Sends two separate digests:
  - Data Analyst/Engineer/BI postings (jobs_raw)      -> DIGEST_TO_EMAIL
  - Test Engineer/QA postings        (jobs_raw_qa)    -> QA_DIGEST_TO_EMAIL

Run locally (after fetch_jobs.py has already run today):
    python ingestion/send_digest.py

Requires environment variables (see ../.env.example):
    DATABASE_URL, GMAIL_ADDRESS, GMAIL_APP_PASSWORD,
    DIGEST_TO_EMAIL, QA_DIGEST_TO_EMAIL
"""

import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.text import MIMEText

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
DIGEST_TO_EMAIL = os.environ["DIGEST_TO_EMAIL"]
QA_DIGEST_TO_EMAIL = os.environ["QA_DIGEST_TO_EMAIL"]

# Postings whose first_seen falls on or after this many hours ago count as
# "new today". 26 hours (not 24) gives a little slack for the cron job
# firing a few minutes late or early without missing/duplicating postings.
LOOKBACK_HOURS = 26

SELECT_NEW_SQL_TEMPLATE = """
SELECT title, company, location, redirect_url, created
FROM {table}
WHERE first_seen >= NOW() - INTERVAL '%s hours'
ORDER BY created DESC NULLS LAST;
"""


def fetch_new_postings(table):
    """Query the given table for postings first seen within the lookback window."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_NEW_SQL_TEMPLATE.format(table=table), (LOOKBACK_HOURS,))
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "title": title,
            "company": company or "Unknown company",
            "location": location or "Bangalore",
            "url": redirect_url,
            "created": created,
        }
        for title, company, location, redirect_url, created in rows
    ]


def build_email_body(postings, profile_label):
    """Plain-text email body listing each new posting with its apply link."""
    today_str = datetime.now(timezone.utc).strftime("%d %b %Y")

    if not postings:
        return (
            f"{profile_label} digest — {today_str}\n\n"
            "No new postings today. The pipeline ran successfully, "
            "there just weren't any fresh matches.\n"
        )

    lines = [f"{profile_label} digest — {today_str}", f"{len(postings)} new posting(s) today:\n"]
    for i, job in enumerate(postings, start=1):
        lines.append(f"{i}. {job['title']} — {job['company']} ({job['location']})")
        lines.append(f"   Apply: {job['url']}\n")

    return "\n".join(lines)


def send_email(to_address, subject, body):
    """Send a digest via Gmail's SMTP server using an app password."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [to_address], msg.as_string())


def send_digest_for(table, profile_label, to_address):
    """Fetch, format, and send one profile's digest."""
    postings = fetch_new_postings(table)
    print(f"[{profile_label}] {len(postings)} posting(s) first seen in the last {LOOKBACK_HOURS}h.")

    body = build_email_body(postings, profile_label)
    send_email(to_address, f"Daily job digest — {profile_label}", body)
    print(f"[{profile_label}] digest sent to {to_address}.")


def main():
    send_digest_for("jobs_raw", "Data Analyst/Engineer", DIGEST_TO_EMAIL)
    send_digest_for("jobs_raw_qa", "Test Engineer/QA", QA_DIGEST_TO_EMAIL)


if __name__ == "__main__":
    sys.exit(main())