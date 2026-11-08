"""
Your profile + what the pipeline searches for.
Edit freely — every nightly run uses whatever is here.
"""

CANDIDATE = {
    "name": "Satish Kumar Reddy Gajjala",
    "location": "Adelaide, Australia",
    "email": "gsatishreddy2001@gmail.com",  # daily briefing lands here
}

# Your experience, projects and skills now live in facts.py (one source of truth for
# scoring, resumes and cover letters). Edit facts.py, not this file.

# ---- What to search for each night (title, where) ----
# 'where' is passed to Adzuna; Jooble uses location too.
# Graduate/intern terms below catch most GradConnection/GradAustralia roles,
# which also post to Seek/Indeed/company pages that Adzuna & Jooble index.
SEARCHES = [
    # --- Testing / QA (all flavours) ---
    {"what": "selenium automation tester",  "where": "Australia"},
    {"what": "java automation engineer",    "where": "Australia"},
    {"what": "qa automation engineer",      "where": "Adelaide"},
    {"what": "test analyst",                "where": "Adelaide"},
    {"what": "software tester",             "where": "Australia"},
    {"what": "qa engineer",                 "where": "Australia"},
    {"what": "graduate test analyst",       "where": "Australia"},
    {"what": "junior software tester",      "where": "Australia"},

    # --- Data Science / Data Analyst / SQL ---
    {"what": "data analyst",                "where": "Adelaide"},
    {"what": "data scientist",              "where": "Adelaide"},
    {"what": "sql analyst",                 "where": "Australia"},
    {"what": "sql developer",               "where": "Australia"},
    {"what": "reporting analyst",           "where": "Australia"},
    {"what": "junior data analyst",         "where": "Australia"},
    {"what": "graduate data analyst",       "where": "Australia"},
    {"what": "data science graduate",       "where": "Australia"},
    {"what": "power bi analyst",            "where": "Australia"},
    {"what": "business intelligence analyst", "where": "Adelaide"},
    {"what": "insurance data analyst",      "where": "Australia"},
    {"what": "data quality analyst",        "where": "Australia"},

    # --- Student-friendly: part-time / casual ---
    {"what": "part time data analyst",      "where": "Australia"},
    {"what": "casual data entry",           "where": "Adelaide"},
    {"what": "part time qa tester",         "where": "Australia"},

    # --- Internships / graduate & vacation programs ---
    {"what": "data analyst intern",         "where": "Australia"},
    {"what": "data science internship",     "where": "Australia"},
    {"what": "software testing internship", "where": "Australia"},
    {"what": "graduate program technology", "where": "Australia"},
    {"what": "graduate program data",       "where": "Australia"},
    {"what": "vacation program",            "where": "Australia"},
    {"what": "summer vacationer program",   "where": "Australia"},
]

# ---- Optional RSS feeds (compliant, no scraping) ----
# Paste any job board / university career-portal RSS URL here and it gets
# pulled, scored and emailed like everything else. Leave empty to skip.
# NOTE: GradConnection / GradAustralia do NOT publish a public feed, so they
# are intentionally not listed — their roles are caught via the searches above.
RSS_FEEDS = [
    # "https://your-university-careerhub.example/feed.rss",
    # "https://someboard.com/categories/data-jobs.rss",
]
