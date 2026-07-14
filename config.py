"""
All knobs live here. Secrets come from environment variables
(set as GitHub Actions secrets — never hard-code them).
"""
import os

# ---- Secrets (from environment) ----
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ADZUNA_APP_ID     = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY    = os.environ.get("ADZUNA_APP_KEY", "")
JOOBLE_KEY        = os.environ.get("JOOBLE_KEY", "")
RESEND_API_KEY    = os.environ.get("RESEND_API_KEY", "")

# ---- Tunables (safe to edit) ----
MODEL          = os.environ.get("MODEL", "claude-sonnet-4-6")  # swap to claude-haiku-4-5 to cut cost ~3x
MAX_NEW_JOBS   = int(os.environ.get("MAX_NEW_JOBS", "25"))     # hard cap on Claude calls per run (cost control)
MIN_FIT_EMAIL  = int(os.environ.get("MIN_FIT_EMAIL", "50"))    # only roles >= this % make the email (inclusive early)
COVER_FIT      = int(os.environ.get("COVER_FIT", "65"))        # write a cover letter only for roles >= this %
TAILOR_FIT     = int(os.environ.get("TAILOR_FIT", "65"))       # generate a tailored resume for roles >= this %
MAX_TAILORED   = int(os.environ.get("MAX_TAILORED", "8"))      # cap tailored resumes per night (cost + email size)
MAX_DAYS_OLD   = int(os.environ.get("MAX_DAYS_OLD", "3"))      # how fresh Adzuna listings must be
PER_QUERY      = int(os.environ.get("PER_QUERY", "12"))        # results to pull per search term per source
COUNTRY        = os.environ.get("ADZUNA_COUNTRY", "au")        # Adzuna country code

# Resend "from" address. With no domain of your own, use the sandbox sender below —
# it can only deliver to the email you registered with Resend.
EMAIL_FROM = os.environ.get("EMAIL_FROM", "JobXpress <onboarding@resend.dev>")

SEEN_FILE = "seen.json"

def missing_keys():
    need = {
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "ADZUNA_APP_ID": ADZUNA_APP_ID,
        "ADZUNA_APP_KEY": ADZUNA_APP_KEY,
        "JOOBLE_KEY": JOOBLE_KEY,
        "RESEND_API_KEY": RESEND_API_KEY,
    }
    return [k for k, v in need.items() if not v]
