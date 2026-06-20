"""
Pulls Data Analyst/Engineer/BI and Test Engineer/QA job postings from the
Adzuna API and upserts them into separate Postgres tables.

Run locally:
    python ingestion/fetch_jobs.py

Requires environment variables (see ../.env.example):
    ADZUNA_APP_ID, ADZUNA_APP_KEY, DATABASE_URL
"""

import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv

from config import (
    KEYWORDS, LOCATION, COUNTRY, RESULTS_PER_PAGE, MAX_PAGES,
    JUNIOR_KEYWORDS, SENIOR_KEYWORDS,
    QA_KEYWORDS, QA_LOCATION, QA_EXPERIENCE_KEYWORDS, QA_SENIOR_KEYWORDS,
)

load_dotenv()

ADZUNA_APP_ID = os.environ["ADZUNA_APP_ID"]
ADZUNA_APP_KEY = os.environ["ADZUNA_APP_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

BASE_URL = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search"

UPSERT_SQL = """
INSERT INTO jobs_raw (
    id, title, company, location, description, salary_min, salary_max,
    contract_type, category, created, redirect_url, raw_json,
    first_seen, last_seen
)
VALUES %s
ON CONFLICT (id) DO UPDATE SET
    last_seen = EXCLUDED.last_seen,
    title = EXCLUDED.title,
    description = EXCLUDED.description;
"""

UPSERT_SQL_QA = UPSERT_SQL.replace("jobs_raw", "jobs_raw_qa")

YEARS_PATTERN = re.compile(r"(\d{1,2})\s*[-+]?\s*(?:to\s*\d{1,2}\s*)?\+?\s*years?", re.IGNORECASE)


def fetch_jobs(keyword, page, location=LOCATION):
    """Call the Adzuna search endpoint for one keyword/page combination."""
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": keyword,
        "where": location,
        "content-type": "application/json",
    }
    resp = requests.get(f"{BASE_URL}/{page}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize(job):
    """Flatten the nested Adzuna response into a row shape matching jobs_raw."""
    return {
        "id": job.get("id"),
        "title": (job.get("title") or "").strip(),
        "company": (job.get("company") or {}).get("display_name"),
        "location": (job.get("location") or {}).get("display_name"),
        "description": job.get("description"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "contract_type": job.get("contract_type"),
        "category": (job.get("category") or {}).get("label"),
        "created": job.get("created"),
        "redirect_url": job.get("redirect_url"),
        "raw_json": job,
    }


def mentions_high_experience(text, threshold=3):
    """
    Returns True if any "<number> year(s)" mention in the text has a
    number >= threshold.
    """
    for match in YEARS_PATTERN.finditer(text):
        years = int(match.group(1))
        if years >= threshold:
            return True
    return False


def matches_experience_profile(job, include_keywords, exclude_keywords, senior_threshold=3):
    """
    A posting is excluded if it numerically mentions senior_threshold+
    years of experience anywhere, OR matches an explicit exclude_keyword.
    Otherwise, included only if it matches at least one include_keyword.
    """
    text = f"{job['title']} {job['description'] or ''}".lower()

    if mentions_high_experience(text, threshold=senior_threshold):
        return False

    if any(term in text for term in exclude_keywords):
        return False

    return any(term in text for term in include_keywords)


def is_junior_friendly(job):
    """Data-role profile: 0-2 years / fresher-level postings."""
    return matches_experience_profile(job, JUNIOR_KEYWORDS, SENIOR_KEYWORDS, senior_threshold=3)


def is_qa_match(job):
    """QA/Test Engineer profile: ~1-3 years, not senior."""
    return matches_experience_profile(job, QA_EXPERIENCE_KEYWORDS, QA_SENIOR_KEYWORDS, senior_threshold=4)


def load_jobs(jobs, upsert_sql=UPSERT_SQL):
    """Upsert a batch of normalized job rows into Postgres."""
    if not jobs:
        print("No jobs to load.")
        return

    now = datetime.now(timezone.utc)
    rows = [
        (
            j["id"], j["title"], j["company"], j["location"], j["description"],
            j["salary_min"], j["salary_max"], j["contract_type"], j["category"],
            j["created"], j["redirect_url"], Json(j["raw_json"]), now, now,
        )
        for j in jobs
        if j["id"]
    ]

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            execute_values(cur, upsert_sql, rows)
        conn.commit()
        print(f"Upserted {len(rows)} postings.")
    finally:
        conn.close()


def fetch_and_dedupe(keywords, location):
    """Run an Adzuna search across all keywords/pages, deduped by id."""
    all_jobs = []
    for keyword in keywords:
        for page in range(1, MAX_PAGES + 1):
            print(f"Fetching '{keyword}' page {page}...")
            try:
                data = fetch_jobs(keyword, page, location=location)
            except requests.HTTPError as exc:
                print(f"  request failed, skipping: {exc}")
                continue

            results = data.get("results", [])
            if not results:
                break

            all_jobs.extend(normalize(job) for job in results)
            time.sleep(1)

    return list({job["id"]: job for job in all_jobs if job["id"]}.values())


def main():
    unique_jobs = fetch_and_dedupe(KEYWORDS, LOCATION)
    print(f"Fetched {len(unique_jobs)} unique data-role postings this run.")

    junior_jobs = [job for job in unique_jobs if is_junior_friendly(job)]
    print(f"{len(junior_jobs)} of those look junior-friendly (0-2 years).")

    load_jobs(junior_jobs, upsert_sql=UPSERT_SQL)

    unique_qa_jobs = fetch_and_dedupe(QA_KEYWORDS, QA_LOCATION)
    print(f"Fetched {len(unique_qa_jobs)} unique QA postings this run.")

    qa_matches = [job for job in unique_qa_jobs if is_qa_match(job)]
    print(f"{len(qa_matches)} of those match the QA experience profile.")

    load_jobs(qa_matches, upsert_sql=UPSERT_SQL_QA)

    print("Done.")


if __name__ == "__main__":
    sys.exit(main())