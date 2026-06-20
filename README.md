# Bangalore Data Jobs Tracker

An end-to-end data engineering pipeline that tracks Data Analyst / Data Engineer /
BI job postings in Bangalore, India — built entirely on free-tier infrastructure.

It pulls live postings daily, lands them in a Postgres warehouse, transforms them
with dbt, and serves a dashboard showing which skills, companies, and trends are
actually moving in the market right now.

## Why this exists

Most beginner data projects stop at "notebook that prints a chart." This one
covers the full lifecycle a real data engineering job actually involves:

- **Ingestion** — calling an external API and handling pagination, rate limits,
  and partial failures
- **Storage** — a real Postgres warehouse with an upsert strategy (not just
  re-writing a CSV)
- **Transformation** — SQL modeled with dbt: staging layer, marts, and
  automated data quality tests
- **Orchestration** — a scheduled, unattended daily run via GitHub Actions
- **Presentation** — a live dashboard, not a static screenshot

## Architecture

```
Adzuna Jobs API
      |
      v
Python ingestion script  (ingestion/fetch_jobs.py)
      |  upserts raw postings
      v
Supabase Postgres        (jobs_raw table)
      |
      v
dbt staging + marts       (dbt_project/models)
      |
      v
Streamlit dashboard       (dashboard/app.py)
```

The whole sequence (ingestion -> dbt run -> test) runs once a day, unattended,
via `.github/workflows/daily_pipeline.yml`.

## Tech stack (all free tier, no card required)

| Layer          | Tool                              |
|----------------|------------------------------------|
| Data source    | Adzuna Jobs API (free developer account) |
| Database       | Supabase Postgres (free tier)      |
| Transformation | dbt Core (open source)             |
| Orchestration  | GitHub Actions (free on public repos) |
| Dashboard      | Streamlit Community Cloud (free hosting) |

## Project layout

```
job-pipeline-project/
├── ingestion/
│   ├── config.py          # keywords, location, skill-keyword dictionary
│   └── fetch_jobs.py       # pulls from Adzuna, upserts into Postgres
├── sql/
│   └── schema.sql          # raw table DDL — run this once in Supabase
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml.example
│   └── models/
│       ├── staging/        # cleaning + skill-flag extraction
│       └── marts/          # skill demand, company hiring, postings trend
├── dashboard/
│   └── app.py               # Streamlit app reading from the marts
├── .github/workflows/
│   └── daily_pipeline.yml   # scheduled ingestion + dbt run
├── requirements.txt
└── .env.example
```

## Setup

1. **Create a Supabase project** (supabase.com, free, no card). Copy the
   connection string from Project Settings -> Database.
2. **Run `sql/schema.sql`** in the Supabase SQL editor to create `jobs_raw`.
3. **Get an Adzuna API key** at developer.adzuna.com (free, instant).
4. **Copy `.env.example` to `.env`** and fill in your credentials.
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Run ingestion once locally** to test: `python ingestion/fetch_jobs.py`
7. **Run dbt**: copy `dbt_project/profiles.yml.example` to `~/.dbt/profiles.yml`,
   fill in your Supabase host/user/password, then `cd dbt_project && dbt run && dbt test`
8. **Run the dashboard**: `streamlit run dashboard/app.py`
9. **Set up the schedule**: add `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `DATABASE_URL`,
   `SUPABASE_HOST`, `SUPABASE_USER`, `SUPABASE_PASSWORD`, `SUPABASE_DBNAME` as
   GitHub Actions secrets in your repo, push, and the daily workflow takes over.
10. **Deploy the dashboard** for free on Streamlit Community Cloud, pointing at
    the same repo, with the same secrets added there.

## What this demonstrates

- Working with REST APIs: auth, pagination, rate limiting, error handling
- Idempotent loading (upsert on conflict, `first_seen` / `last_seen` tracking)
- Data modeling with dbt: sources, staging, marts, tests
- SQL skills: window-free aggregation, `date_trunc`, conditional aggregation
- Scheduling and orchestration with CI/CD tooling
- Building and deploying a live, queryable dashboard

## Possible extensions

- Add salary trend analysis once enough postings have salary data
- Track posting "lifespan" (days between `first_seen` and last appearance)
- Add a second data source (e.g. RemoteOK or Arbeitnow API) and a `source`
  column to compare postings across platforms
- Swap GitHub Actions for a lightweight Airflow/Dagster deployment as a v2
