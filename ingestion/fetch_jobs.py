"""
Pulls Data Analyst / Data Engineer / BI job postings from the Adzuna API
and upserts them into a Postgres `jobs_raw` table.

Run locally:
    python ingestion/fetch_jobs.py

Requires environment variables (see ../.env.example):
    ADZUNA_APP_ID, ADZUNA_APP_KEY, DATABASE_URL
"""

import os
import sys
import time
from datetime import datetime, timezone

import requests
import psycopg2
from psycopg2.extras import execute_values, Json
from dotenv import load_dotenv

from config import KEYWORDS, LOCATION, COUNTRY, RESULTS_PER_PAGE, MAX_PAGES

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


def fetch_jobs(keyword, page):
    """Call the Adzuna search endpoint for one keyword/page combination."""
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": keyword,
        "where": LOCATION,
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


def load_jobs(jobs):
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
        if j["id"]  # skip anything missing a stable id
    ]

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            execute_values(cur, UPSERT_SQL, rows)
        conn.commit()
        print(f"Upserted {len(rows)} postings.")
    finally:
        conn.close()


def main():
    all_jobs = []
    for keyword in KEYWORDS:
        for page in range(1, MAX_PAGES + 1):
            print(f"Fetching '{keyword}' page {page}...")
            try:
                data = fetch_jobs(keyword, page)
            except requests.HTTPError as exc:
                print(f"  request failed, skipping: {exc}")
                continue

            results = data.get("results", [])
            if not results:
                break  # no more pages for this keyword

            all_jobs.extend(normalize(job) for job in results)
            time.sleep(1)  # stay polite on the free tier

    # The same posting often matches multiple keywords — keep one copy.
    unique_jobs = list({job["id"]: job for job in all_jobs if job["id"]}.values())
    print(f"Fetched {len(unique_jobs)} unique postings this run.")

    load_jobs(unique_jobs)
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
