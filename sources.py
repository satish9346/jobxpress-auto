"""
Job sources. Both are official, free aggregator APIs — no scraping,
no login, ToS-friendly. They surface listings that originate on
Seek / Indeed / LinkedIn / company sites.
"""
import hashlib
import re

import requests
import config

TIMEOUT = 25


def _jid(title, company, url):
    """Stable id for de-duplication across sources."""
    base = (title or "").lower().strip() + "|" + (company or "").lower().strip()
    if url:
        base = url.split("?")[0].lower()
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


AU_PLACES = ["australia", "adelaide", "sydney", "melbourne", "brisbane", "perth", "canberra", "hobart",
             "darwin", "gold coast", "newcastle", "wollongong", "geelong", "sunshine coast", "townsville",
             "cairns", "toowoomba", "ballarat", "bendigo", "launceston", "mawson lakes", "port adelaide"]
AU_STATE_NAMES = ["new south wales", "victoria", "queensland", "western australia", "south australia",
                  "tasmania", "northern territory", "australian capital territory"]
AU_CODES = ["nsw", "vic", "qld", "sa", "tas", "act", "nt"]          # "wa" handled separately (clashes with Washington)
FOREIGN = ["united states", "usa", "u.s.", "canada", "united kingdom", " uk", "england", "india", "new zealand",
           "singapore", "philippines", "seattle", "redmond", "bellevue", "new york", "california", "texas",
           "london", "toronto", "bangalore", "bengaluru", "hyderabad", "auckland", "dubai"]
US_STATE = re.compile(r",\s*(A[LKZR]|C[AOT]|DE|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|"
                      r"PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY]|DC)\b")


def is_australian(location, text=""):
    """True for Australian or unspecified locations. Overseas roles waste applications."""
    loc = (location or "").strip()
    ll = f" {loc.lower()} "
    if not loc:
        blob = (text or "").lower()
        return not any(w in blob for w in ["seattle", "united states", " usa ", "h-1b", "green card"])
    if any(f in ll for f in FOREIGN) or (US_STATE.search(loc) and "perth" not in ll):
        return False
    if any(p in ll for p in AU_PLACES + AU_STATE_NAMES):
        return True
    if any(re.search(r"\b" + c + r"\b", ll) for c in AU_CODES):
        return True
    if re.search(r"\bwa\b", ll):                    # only Western Australia if nothing points overseas
        return not US_STATE.search(loc)
    return "remote" in ll and "australia" in (text or "").lower()


def _clean(text, limit=4000):
    if not text:
        return ""
    return " ".join(text.split())[:limit]


def fetch_adzuna(what, where):
    """https://developer.adzuna.com — free tier."""
    url = f"https://api.adzuna.com/v1/api/jobs/{config.COUNTRY}/search/1"
    params = {
        "app_id": config.ADZUNA_APP_ID,
        "app_key": config.ADZUNA_APP_KEY,
        "what": what,
        "where": where,
        "results_per_page": config.PER_QUERY,
        "max_days_old": config.MAX_DAYS_OLD,
        "sort_by": "date",
        "content-type": "application/json",
    }
    out = []
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        for j in r.json().get("results", []):
            company = (j.get("company") or {}).get("display_name", "")
            loc = (j.get("location") or {}).get("display_name", "")
            link = j.get("redirect_url", "")
            title = j.get("title", "")
            out.append({
                "id": _jid(title, company, link),
                "title": title,
                "company": company,
                "location": loc,
                "desc": _clean(j.get("description", "")),
                "link": link,
                "source": "Adzuna",
            })
    except Exception as e:
        print(f"  [Adzuna] '{what}' failed: {e}")
    return out


def fetch_jooble(what, where):
    """https://jooble.org/api/about — one key, POST JSON."""
    url = f"https://jooble.org/api/{config.JOOBLE_KEY}"
    out = []
    try:
        r = requests.post(url, json={"keywords": what, "location": where}, timeout=TIMEOUT)
        r.raise_for_status()
        for j in r.json().get("jobs", [])[: config.PER_QUERY]:
            title = j.get("title", "")
            company = j.get("company", "")
            link = j.get("link", "")
            loc = j.get("location", "") or ""
            out.append({
                "id": _jid(title, company, link),
                "title": title,
                "company": company,
                "location": loc,
                "desc": _clean(j.get("snippet", "")),
                "link": link,
                "source": "Jooble",
            })
    except Exception as e:
        print(f"  [Jooble] '{what}' failed: {e}")
    return out


def fetch_rss(url):
    """Generic RSS/Atom fetcher — works with any compliant job feed."""
    out = []
    try:
        import feedparser
        feed = feedparser.parse(url)
        for e in feed.entries[: config.PER_QUERY]:
            title = getattr(e, "title", "")
            link = getattr(e, "link", "")
            # description lives under summary or content depending on the feed
            desc = getattr(e, "summary", "") or ""
            if getattr(e, "content", None):
                desc = e.content[0].get("value", desc)
            company = getattr(e, "author", "") or ""
            out.append({
                "id": _jid(title, company, link),
                "title": title,
                "company": company,
                "location": "",
                "desc": _clean(desc),
                "link": link,
                "source": "RSS",
            })
    except Exception as e:
        print(f"  [RSS] {url[:40]} failed: {e}")
    return out


def gather(searches, rss_feeds=None):
    """Run every search across both APIs + any RSS feeds, de-duplicate."""
    seen, jobs = set(), []
    for s in searches:
        what, where = s["what"], s["where"]
        print(f"  searching: {what} @ {where}")
        for job in fetch_adzuna(what, where) + fetch_jooble(what, where):
            if not job["title"] or job["id"] in seen:
                continue
            seen.add(job["id"])
            jobs.append(job)
    if config.AUSTRALIA_ONLY:
        before = len(jobs)
        jobs = [j for j in jobs if is_australian(j["location"], j["desc"])]
        print(f"  dropped {before - len(jobs)} overseas listings")
    for url in (rss_feeds or []):
        print(f"  rss: {url[:50]}")
        for job in fetch_rss(url):
            if not job["title"] or job["id"] in seen:
                continue
            seen.add(job["id"])
            jobs.append(job)
    return jobs
