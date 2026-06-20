# Configuration for the job ingestion script.
# Edit these to widen/narrow the search without touching the script logic.

# Search terms run against the Adzuna "what" parameter.
KEYWORDS = [
    "data analyst",
    "data engineer",
    "business intelligence",
    "data scientist",
    "SQL developer",
]

# Adzuna "where" parameter. Keep broad-ish ("Bangalore") rather than a
# specific neighborhood, or you will miss postings.
LOCATION = "Bangalore"

# Adzuna country code. "in" = India. See developer.adzuna.com for the full list.
COUNTRY = "in"

# Adzuna allows up to 50 results per page on the free tier.
RESULTS_PER_PAGE = 50

# Keep this small to stay comfortably inside free-tier rate limits.
# 2 pages x 5 keywords = 10 requests per run, once a day.
MAX_PAGES = 2

# Keyword -> list of substrings to search for (case-insensitive) inside the
# combined title + description text. Used to flag which skills a posting
# mentions. Extend this dictionary as you notice new tools coming up often.
SKILL_KEYWORDS = {
    "sql": ["sql"],
    "python": ["python"],
    "power_bi": ["power bi", "powerbi"],
    "excel": ["excel"],
    "snowflake": ["snowflake"],
    "airflow": ["airflow"],
    "dbt": ["dbt"],
    "spark": ["spark", "pyspark"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "tableau": ["tableau"],
    "sap_stack": ["sap", "bods", "businessobjects"],
}

# Phrases that suggest a posting wants entry-level / 0-2 years experience.
# Checked against the combined title + description text (case-insensitive).
JUNIOR_KEYWORDS = [
    "fresher", "freshers", "entry level", "entry-level",
    "0-1 year", "0-2 year", "0-2 years", "1-2 years",
    "trainee", "graduate program", "associate analyst",
    "junior", "intern",
]

# Phrases that suggest a posting wants 3+ years experience.
# If any of these appear, we treat the posting as NOT junior, even if a
# JUNIOR_KEYWORDS phrase also appears (descriptions often list both).
SENIOR_KEYWORDS = [
    "senior", "lead", "principal", "5+ years", "7+ years",
    "minimum 3 years", "minimum 4 years", "minimum 5 years",
    "3-5 years", "4-6 years", "5-8 years", "manager",
]

# --- Second job profile: Test Engineer / QA, ~2 years experience ---

# Search terms for the QA/Test Engineer profile (separate Adzuna search).
QA_KEYWORDS = [
    "test engineer",
    "QA engineer",
    "software tester",
    "automation tester",
    "SDET",
]

# Same location/country as the data-role search — change if your friend
# wants a different city.
QA_LOCATION = "Bangalore"

# Phrases suggesting roughly 1-3 years experience (not a fresher, not senior).
# Unlike JUNIOR_KEYWORDS, this profile does NOT match on "fresher"/"intern"
# since your friend already has ~1.9 years and isn't looking for entry-level.
QA_EXPERIENCE_KEYWORDS = [
    "1-2 years", "1-3 years", "2-3 years", "1.5 years",
    "2 years", "2+ years", "1+ year",
]

# Same senior-exclusion logic as the data-role profile.
QA_SENIOR_KEYWORDS = [
    "senior", "lead", "principal", "5+ years", "7+ years",
    "minimum 3 years", "minimum 4 years", "minimum 5 years",
    "3-5 years", "4-6 years", "5-8 years", "manager",
]