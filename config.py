"""
All knobs live here. Secrets come from environment variables
(set as GitHub Actions secrets — never hard-code them).
"""
import os

# ---- Secrets (from environment) ----  .strip() removes stray spaces/newlines
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
ADZUNA_APP_ID     = os.environ.get("ADZUNA_APP_ID", "").strip()
ADZUNA_APP_KEY    = os.environ.get("ADZUNA_APP_KEY", "").strip()
JOOBLE_KEY        = os.environ.get("JOOBLE_KEY", "").strip()
RESEND_API_KEY    = os.environ.get("RESEND_API_KEY", "").strip()

# ---- FREE MODE ----  set to "1" to skip ALL AI (no cost): just fetch + email raw listings.
FREE_MODE      = os.environ.get("FREE_MODE", "0").strip() == "1"

# ---- Tunables (safe to edit) ----
MODEL          = os.environ.get("MODEL", "claude-haiku-5-5")   # cheap model, scores every job
WRITE_MODEL    = os.environ.get("WRITE_MODEL", "claude-sonnet-5-5")  # writes resumes + cover letters (top jobs only)
MAX_NEW_JOBS   = int(os.environ.get("MAX_NEW_JOBS", "20"))     # hard cap on Claude calls per run (cost control)
MIN_FIT_EMAIL  = int(os.environ.get("MIN_FIT_EMAIL", "45"))    # only roles >= this % make the email
COVER_FIT      = int(os.environ.get("COVER_FIT", "62"))        # write a cover letter for roles >= this %
TAILOR_FIT     = int(os.environ.get("TAILOR_FIT", "62"))       # tailor a resume for roles >= this %
MAX_TAILORED   = int(os.environ.get("MAX_TAILORED", "5"))      # cap tailored packs per run (about 6 US cents each)
AUSTRALIA_ONLY = os.environ.get("AUSTRALIA_ONLY", "1").strip() != "0"  # drop overseas jobs before scoring
MAX_DAYS_OLD   = int(os.environ.get("MAX_DAYS_OLD", "10"))      # how fresh Adzuna listings must be
PER_QUERY      = int(os.environ.get("PER_QUERY", "20"))        # results per search term per source
COUNTRY        = os.environ.get("ADZUNA_COUNTRY", "au")        # Adzuna country code

# Student-friendly role types that get a priority boost in ranking
PRIORITY_TYPES = ["part-time", "casual", "vacation", "internship", "graduate program"]

# Resend "from" address. With no domain of your own, use the sandbox sender below —
# it can only deliver to the email you registered with Resend.
EMAIL_FROM = os.environ.get("EMAIL_FROM", "JobXpress <onboarding@resend.dev>")

SEEN_FILE = "seen.json"
CSV_FILE  = "applications.csv"   # running tracker, committed back each run

def missing_keys():
    need = {
        "ADZUNA_APP_ID": ADZUNA_APP_ID,
        "ADZUNA_APP_KEY": ADZUNA_APP_KEY,
        "JOOBLE_KEY": JOOBLE_KEY,
        "RESEND_API_KEY": RESEND_API_KEY,
    }
    if not FREE_MODE:                       # AI key only needed when scoring
        need["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    return [k for k, v in need.items() if not v]
