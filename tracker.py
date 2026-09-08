"""
Appends every emailed match to applications.csv so you have one master
list to open in Excel. The GitHub Action commits this file back each run,
so it grows over time. 'Status' starts as 'Emailed' — you update it
yourself in Excel (Applied / Interview / Rejected / Offer).
"""
import csv
import os
from datetime import datetime
import config

HEADERS = ["date", "status", "category", "fit", "route", "title",
           "company", "location", "source", "apply_link", "careers_search"]

def _careers_search(job):
    """A Google link to the company's own careers page for this role —
    direct applications get better ATS pickup than aggregator redirects."""
    from urllib.parse import quote_plus
    q = quote_plus(f'{job.get("company","")} careers {job.get("title","")}')
    return f"https://www.google.com/search?q={q}"

def append(matches):
    if not matches:
        return
    exists = os.path.exists(config.CSV_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(config.CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(HEADERS)
        for j in matches:
            a = j.get("analysis", {})
            w.writerow([
                today, "Emailed", a.get("category", "Job"),
                a.get("fit_score", ""), a.get("recommended_profile", ""),
                j.get("title", ""), j.get("company", ""), j.get("location", ""),
                j.get("source", ""), j.get("link", ""), _careers_search(j),
            ])


def append_free(jobs):
    """Free-mode logging — no AI fields, just the listing facts."""
    if not jobs:
        return
    exists = os.path.exists(config.CSV_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(config.CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(HEADERS)
        for j in jobs:
            w.writerow([
                today, "Listed", "", "", "",
                j.get("title", ""), j.get("company", ""), j.get("location", ""),
                j.get("source", ""), j.get("link", ""), _careers_search(j),
            ])
