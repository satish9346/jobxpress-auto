"""
Your profile + what the pipeline searches for.
Edit freely — every nightly run uses whatever is here.
"""

CANDIDATE = {
    "name": "Satish Kumar Reddy Gajjala",
    "location": "Adelaide, Australia",
    "email": "gsatishreddy2001@gmail.com",  # daily briefing lands here
}

# ---- The two profiles Claude matches each job against ----
PROFILE_DS = """\
MASTER OF DATA SCIENCE (in progress) — University of Adelaide, 2025
B.Tech ECE — Sree Vidyanikethan Engineering College (8.5/10), 2023

EXPERIENCE — Cognizant (Software Engineer, Dec 2023 - Aug 2025)
- MetLife: Analysed/validated 50,000+ policyholder records with SQL & Excel, improved data accuracy 80%.
  Automated data-cleaning in Python (saved 80+ hrs/month). Built Power BI dashboards for claims, renewals,
  premiums. Delivered weekly stakeholder insights.
- VOYA: SQL + Python for backend data-pattern analysis & data-quality checks. Validated data flows & reporting.

SKILLS: Python, SQL, Java | Pandas, NumPy, Excel(adv) | Power BI, Tableau, Matplotlib, Seaborn |
Scikit-learn (regression, classification, clustering) | TensorFlow/Keras, LSTM, CNN, VGG16, ResNet50,
InceptionV3 | Statistics, feature engineering, predictive modelling | Jupyter, Git

PROJECTS: NSE/Nifty-50 analysis (Python/Pandas) | Pneumonia detection VGG16/CNN 98.4% |
Fake-news detection NLP/TF-IDF 94.3% | Weed identification CNN/OpenCV

CERTS: IBM Data Analyst, Neural Networks & Deep Learning, Predictive Modeling, Power BI, Time Series
"""

PROFILE_QA = """\
MASTER OF DATA SCIENCE (in progress) — University of Adelaide, 2025
B.Tech ECE — Sree Vidyanikethan Engineering College (8.5/10), 2023

EXPERIENCE — Cognizant (Software Engineer, Dec 2023 - Aug 2025)
- VOYA (insurance platform): Automated 500+ test cases with Selenium WebDriver (Java) — regression
  efficiency +75%. Data-driven testing with Apache POI (-60% manual effort). Integrated TestNG + Cucumber
  BDD (95% coverage). Logged 250+ defects -> 40% faster releases.
- MetLife: SQL/Excel validation of 50,000+ records, Python automation, Power BI reporting.

SKILLS: Selenium WebDriver(Java), TestNG, Cucumber BDD, Maven, Jenkins, CI/CD | Manual testing, test
cases, defect reporting, Jira, Confluence | API testing: Postman, REST, JSON, XML | Java, Python |
SQL, MySQL | ExtentReports

PROJECTS: Automating Practo.com hospital search (Selenium/Java/TestNG/ExtentReports) — cross-browser, CSV-driven

CERTS: Selenium WebDriver with Java (Advanced), Cucumber BDD Framework
"""

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
