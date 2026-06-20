-- Run this once in the Supabase SQL editor before the first ingestion run.

CREATE TABLE IF NOT EXISTS jobs_raw (
    id              TEXT PRIMARY KEY,
    title           TEXT,
    company         TEXT,
    location        TEXT,
    description     TEXT,
    salary_min      NUMERIC,
    salary_max      NUMERIC,
    contract_type   TEXT,
    category        TEXT,
    created         TIMESTAMPTZ,
    redirect_url    TEXT,
    raw_json        JSONB,
    first_seen      TIMESTAMPTZ NOT NULL,
    last_seen       TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_raw_created ON jobs_raw (created);
CREATE INDEX IF NOT EXISTS idx_jobs_raw_company ON jobs_raw (company);
