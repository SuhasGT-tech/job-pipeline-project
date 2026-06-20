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
