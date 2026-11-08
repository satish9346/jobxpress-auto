"""
MASTER FACTS: the single source of truth for every resume and cover letter.

The Resume Tailor agent may only SELECT and REWORD what is here. It cannot add
employers, dates, numbers, tools or qualifications. Code checks every number and
skill in its output against this file, and anything that does not match is
replaced with the original wording.

Keep this file true. Lines marked CONFIRM need checking.

Private details (phone) come from GitHub secrets, not from this file, because
this repository is public.
"""
import os

CONTACT = {
    "name": "Satish Kumar Reddy Gajjala",
    "location": "Adelaide, SA",
    "email": "gsatishreddy2001@gmail.com",
    "phone": os.environ.get("CANDIDATE_PHONE", "").strip(),          # GitHub secret
    "linkedin": "linkedin.com/in/satish-kumar-reddy-gajjala-450150234",
    "github": "github.com/satish9346",
    "portfolio": os.environ.get("PORTFOLIO_URL", "").strip(),         # e.g. satish9346.github.io
}

# Shown under the contact line. Australian recruiters screen on this first.
WORK_RIGHTS = os.environ.get(
    "WORK_RIGHTS",
    "Student visa with work rights (part time in semester, full time in breaks); "
    "eligible for a 485 Temporary Graduate visa with full work rights from mid 2027",
).strip()

# Headline titles the agent may choose from (it may not invent a new title).
HEADLINES = {
    "data": ["Data Analyst", "Junior Data Analyst", "Graduate Data Analyst", "Data Scientist (Graduate)",
             "Reporting Analyst", "BI Analyst", "SQL Analyst"],
    "qa": ["QA Automation Engineer", "Test Automation Engineer", "Test Analyst", "Software Tester",
           "QA Engineer", "Graduate Test Analyst"],
}

EDUCATION = [
    {"id": "edu_msc", "degree": "Master of Data Science", "school": "Adelaide University",
     "location": "Adelaide, SA", "dates": "Sep 2025 – Jul 2027 (expected)",
     "detail": "Machine learning, LLMs and applications, data taming and prediction, data visualisation"},
    {"id": "edu_btech", "degree": "Bachelor of Technology, Electronics and Communication Engineering",
     "school": "Sree Vidyanikethan Engineering College", "location": "India", "dates": "2019 – 2023",
     "detail": "GPA 8.5/10"},
]

# Each job: fixed header fields (rendered by code, never by the model) + bullets the model can pick.
EXPERIENCE = [
    {
        "id": "cognizant",
        "employer": "Cognizant",
        "location": "Hyderabad, India",
        "title": "Program Analyst (QA Automation and Data)",   # CONFIRM title shown on LinkedIn
        "dates": "Dec 2023 – Aug 2025",                         # CONFIRM end month (LinkedIn shows Sep 2025)
        "months": 21,
        "bullets": [
            # MetLife (insurance data)
            {"id": "m1", "track": "data", "client": "MetLife",
             "text": "Validated 50,000+ MetLife policyholder records across systems using SQL and Excel, improving data accuracy by 80%."},
            {"id": "m2", "track": "data", "client": "MetLife",
             "text": "Automated data cleaning in Python, saving 80+ hours of manual work a month."},
            {"id": "m3", "track": "data", "client": "MetLife",
             "text": "Built Power BI dashboards for claims, renewals and premiums, and delivered weekly insights to stakeholders."},
            # VOYA (financial services, QA automation and data checks)
            {"id": "v1", "track": "qa", "client": "VOYA",
             "text": "Automated 500+ test cases with Selenium WebDriver and Java for VOYA's insurance platform, improving regression efficiency by 75% and speeding up releases by 40%."},
            {"id": "v2", "track": "qa", "client": "VOYA",
             "text": "Implemented data-driven testing with Apache POI, cutting manual testing effort by 60%."},
            {"id": "v3", "track": "qa", "client": "VOYA",
             "text": "Integrated TestNG and Cucumber BDD into the framework, lifting test coverage to 95%."},
            {"id": "v4", "track": "both", "client": "VOYA",
             "text": "Validated cross-system data flows with SQL and Python, logging 250+ defects in Jira."},
            {"id": "v5", "track": "qa", "client": "VOYA",
             "text": "Ran automated suites in Jenkins CI/CD pipelines with Maven, working in Agile sprints with developers and analysts."},
        ],
    },
    {
        "id": "woolworths",
        "employer": "Woolworths Primary Connect",
        "location": "Adelaide, SA",
        "title": "Warehouse Team Member (part time, alongside study)",
        "dates": "Oct 2025 – Present",
        "months": 0,   # not counted as professional tech experience
        "bullets": [
            {"id": "w1", "track": "both", "client": "",
             "text": "Work morning shifts in a high-volume distribution centre, building Australian workplace experience alongside full-time study."},   # ADD a real achievement
        ],
    },
]

PROJECTS = [
    {"id": "p_agents", "track": "both", "name": "Career Agents (AI job-search system)",
     "text": "Built a multi-agent system in Python with the Claude Agent SDK that finds jobs through APIs, scores fit, researches companies with three subagents and tailors applications, with human approval and a monthly cost cap.",
     "tools": ["Python", "Claude Agent SDK", "SQLite", "GitHub Actions"]},
    {"id": "p_roads", "track": "data", "name": "Australian road fatalities analysis",
     "text": "Cleaned and analysed 58,389 ARDD and BITRE fatality records (1989–2026) in R; built bar, grouped-bar and heatmap views showing that afternoon and evening peak-traffic periods carry the most fatalities.",
     "tools": ["R", "ggplot2", "tidyverse"]},
    {"id": "p_llm", "track": "data", "name": "Fine-tuning language models",
     "text": "Fine-tuned BERT for Yelp star-rating prediction (0.586 accuracy vs 0.494 for Flan-T5 across 10 seeds) and compared BART and Flan-T5 summaries with ROUGE and BERTScore.",
     "tools": ["Python", "Hugging Face", "BERT", "Flan-T5", "BART"]},
    {"id": "p_telco", "track": "data", "name": "Telco complaint analytics",
     "text": "Built a Tableau decision-support dashboard on public ACMA and TIO data comparing complaint resolution and escalation rates.",
     "tools": ["Tableau"]},
    {"id": "p_pneumonia", "track": "data", "name": "Pneumonia detection from chest X-rays",
     "text": "Trained a VGG16-based CNN with transfer learning that reached 98.4% accuracy.",
     "tools": ["Python", "TensorFlow", "Keras", "CNN"]},
    {"id": "p_fakenews", "track": "data", "name": "Fake news detection",
     "text": "Built an NLP classifier with TF-IDF features that reached 94.3% accuracy.",
     "tools": ["Python", "scikit-learn", "NLP"]},
    {"id": "p_nifty", "track": "data", "name": "NSE Nifty-50 market analysis",
     "text": "Analysed Nifty-50 index data in Python and Pandas to explore trends and volatility.",
     "tools": ["Python", "Pandas"]},
    {"id": "p_practo", "track": "qa", "name": "Practo.com hospital search automation",
     "text": "Automated cross-browser hospital search tests with Selenium, Java and TestNG, using CSV-driven test data and ExtentReports.",
     "tools": ["Selenium", "Java", "TestNG", "ExtentReports"]},
]

SKILLS = {
    "Languages": ["Python", "SQL", "R", "Java"],
    "Data and analysis": ["Pandas", "NumPy", "Excel", "MySQL", "Statistics", "Regression", "ANOVA",
                          "Hypothesis testing", "Feature engineering", "Predictive modelling", "Data validation",
                          "Data cleaning", "Data quality"],
    "Visualisation and BI": ["Power BI", "Tableau", "Matplotlib", "Seaborn", "ggplot2", "Dashboards", "Reporting"],
    "Machine learning and AI": ["scikit-learn", "TensorFlow", "Keras", "CNN", "LSTM", "Transfer learning",
                                "NLP", "Hugging Face", "BERT", "LLMs", "Claude Agent SDK", "Classification",
                                "Clustering"],
    "Testing and QA": ["Selenium WebDriver", "TestNG", "Cucumber BDD", "Apache POI", "Manual testing",
                       "Test case design", "Defect reporting", "Regression testing", "API testing", "Postman",
                       "REST", "JSON", "XML", "ExtentReports"],
    "Tools and delivery": ["Git", "GitHub Actions", "Jenkins", "Maven", "CI/CD", "Jira", "Confluence",
                           "Agile", "Jupyter", "Quarto"],
}

CERTIFICATIONS = [
    "IBM Data Analyst Professional Certificate",
    "Neural Networks and Deep Learning",
    "Predictive Modeling",
    "Power BI",
    "Time Series Analysis",
    "Selenium WebDriver with Java (Advanced)",
    "Cucumber BDD Framework",
]
IN_PROGRESS = ["Microsoft PL-300 Power BI Data Analyst (in progress)"]

LANGUAGES = ["English", "Telugu"]


# ---------- helpers used by the agent and the scorer ----------
def all_bullets():
    return {b["id"]: (job, b) for job in EXPERIENCE for b in job["bullets"]}


def all_skills():
    return {s.lower(): s for group in SKILLS.values() for s in group} | \
           {t.lower(): t for p in PROJECTS for t in p["tools"]}


def corpus():
    """All fact text, used to check that every number in the output is real."""
    parts = [WORK_RIGHTS]
    parts += [f"{e['degree']} {e['school']} {e['dates']} {e['detail']}" for e in EDUCATION]
    for job in EXPERIENCE:
        parts.append(f"{job['employer']} {job['title']} {job['dates']} {job['months']} months")
        parts += [b["text"] for b in job["bullets"]]
    parts += [p["text"] for p in PROJECTS]
    parts += CERTIFICATIONS + IN_PROGRESS
    return "\n".join(parts)


def tech_months():
    return sum(j["months"] for j in EXPERIENCE)


def profile_text(track):
    """Plain-text profile for the job scorer, built from the facts above."""
    lines = [f"EDUCATION: " + "; ".join(f"{e['degree']}, {e['school']} ({e['dates']})" for e in EDUCATION),
             f"PROFESSIONAL EXPERIENCE: {tech_months()} months in industry"]
    for job in EXPERIENCE:
        lines.append(f"{job['title']}, {job['employer']}, {job['location']} ({job['dates']})")
        for b in job["bullets"]:
            if track in (b["track"], "all") or b["track"] == "both":
                lines.append(f"- {b['text']}")
    lines.append("PROJECTS:")
    lines += [f"- {p['name']}: {p['text']}" for p in PROJECTS if track in (p["track"], "all") or p["track"] == "both"]
    lines.append("SKILLS: " + " | ".join(", ".join(v) for v in SKILLS.values()))
    lines.append("CERTIFICATIONS: " + ", ".join(CERTIFICATIONS))
    lines.append(f"LOCATION AND WORK RIGHTS: {CONTACT['location']}. {WORK_RIGHTS}")
    return "\n".join(lines)
