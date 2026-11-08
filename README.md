# JobXpress — your automatic job-finding pipeline

Every night this:
1. **Finds** fresh Data Science + QA roles across Australia (Adzuna + Jooble APIs — legal aggregators covering Seek, Indeed, LinkedIn & thousands of company career pages, plus any RSS feeds you add).
2. **Scores** each with Claude against your two resumes (DS and QA), picks the better-fit resume, flags gaps, and classifies it as **Internship / Graduate program / Job**.
3. **Writes** a ready-to-send cover letter for strong matches.
4. **Tailors your resume per job** for the top matches — summary, skill order and bullet emphasis rewritten to mirror that job's description (facts never invented) — attached to the email as Word and PDF files.
5. **Emails** you one briefing, grouped Internships → Graduate programs → Jobs, each with fit %, reasons, gaps, Apply link, cover letter, and tailored resume attached.

You wake up, open the email, click **Apply** on the best few. The clicking stays with you — that's deliberate. Bots that auto-submit get Seek/LinkedIn/Indeed accounts **banned**, and auto-filled applications get auto-rejected. This tool kills the slow 90% (searching, matching, writing) and keeps you safe and in control.

No passwords for any job board are ever used or needed.

---


## New: Resume Tailor agent (Nov 2026)

For each top match, JobXpress now attaches a **tailored resume and cover letter in Word (.docx) and PDF**, plus an ATS keyword report.

**How it works**
1. `facts.py` holds every true fact about you: jobs, dates, numbers, projects, skills. It is the only source the agent can use.
2. `resume_agent.py` reads the job ad, pulls out its keywords, and writes a tailored headline, summary, skills order, bullets, projects and cover letter (Claude Sonnet, top 5 jobs per run).
3. Code then **checks every claim**: unknown bullets are dropped, changed numbers are reverted, invented numbers and phrases like "G'day" or "visa sponsorship" are removed, and "two years" becomes your exact 21 months.
4. `docgen.py` renders an Australian, ATS-friendly layout: single column, no tables or photo, contact details in the body, a work-rights line, standard headings, A4.
5. The email shows the **keyword match %**, keywords you could add (only if true), and real gaps.

**Overseas jobs are now filtered out.** The old Jooble filter accepted "Seattle, WA" as Western Australia. `sources.is_australian()` now drops US and other overseas listings before scoring (set the variable `AUSTRALIA_ONLY=0` to turn this off).

**Tailor any job yourself** (from Seek, LinkedIn or a company site): save the ad as a text file and run
```bash
python tailor_job.py job.txt --company "SA Water" --title "Graduate Data Analyst"
```
Files and a `match_report.txt` appear in `output/`.

**New settings**
| Name | Where | What |
| --- | --- | --- |
| `CANDIDATE_PHONE` | Actions **secret** | Your mobile number for the resume header (kept out of this public repo) |
| `WORK_RIGHTS` | Actions variable (optional) | Overrides the work-rights line |
| `PORTFOLIO_URL` | Actions variable (optional) | e.g. `satish9346.github.io` |
| `WRITE_MODEL` | Actions variable (optional) | Model for resumes, default `claude-sonnet-5-5` |
| `MAX_TAILORED` | Actions variable (optional) | Packs per run, default 5 (about 6 US cents each) |

**Keep `facts.py` true and current.** Lines marked CONFIRM need checking.

## What's new in this version
- **PDF attachments** — tailored resume AND cover letter arrive as clean, ATS-friendly PDFs (still read each one before sending — you're accountable for every word).
- **Application tracker** — every emailed match is appended to `applications.csv` in the repo. Open it in Excel; update the `status` column yourself (Applied / Interview / Rejected / Offer). It grows over time.
- **"Find on company site" link** — each job gets a Google link to the company's own careers page, which usually gives better ATS pickup than aggregator redirects.
- **Student-priority ranking** — part-time, casual, internships, vacation programs and graduate programs are flagged and sorted to the top of the email.


## Two ways to run — paid (AI) or FREE

**Default = cheap AI mode:** uses claude-haiku-4-5 (≈3× cheaper than Sonnet), scores up to 20 jobs, runs every 3 days. A few dollars lasts weeks. Top up at console.anthropic.com → Billing.

**FREE mode (no AI, $0):** add a GitHub secret named `FREE_MODE` with value `1`. The pipeline then skips all AI — it just fetches new listings and emails them to you with Apply + "company site" links, and logs them to applications.csv. No Anthropic credits needed. Paste any interesting role into the dashboard for a fit score + cover letter. To go back to AI mode, delete the `FREE_MODE` secret (or set it to `0`).

## What you need (all free tiers)

| Key | Where to get it | Free? |
|-----|-----------------|-------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → Settings → API keys | pay-per-use, cents/day |
| `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | developer.adzuna.com → register an app | free |
| `JOOBLE_KEY` | jooble.org/api/about → request a key | free |
| `RESEND_API_KEY` | resend.com → API Keys | free (100 emails/day) |

**Resend note:** with no domain of your own, leave `EMAIL_FROM` as the default `onboarding@resend.dev`. Resend will deliver to the email address you signed up with — make sure that's the inbox in `profile.py`. (To send from your own address later, verify a domain in Resend.)

---

## Option A — fully automatic (recommended): GitHub Actions

1. Create a new **private** GitHub repo and upload all these files.
2. Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add each key from the table above (names must match exactly).
3. That's it. The workflow in `.github/workflows/daily.yml` runs every night at ~09:00 UTC (7:30pm Adelaide). Change the `cron` line to retime it.
4. Want to test immediately? Repo → **Actions → JobXpress daily run → Run workflow**.

It's free: GitHub Actions gives 2,000 free minutes/month; each run takes ~2 minutes.

## Option B — run it yourself

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your real keys
python run_local.py
```

---

## Make it yours

- **Different jobs / cities** → edit `SEARCHES` in `profile.py`.
- **Add a job board's RSS feed** → drop its URL into `RSS_FEEDS` in `profile.py`. (Note: GradConnection & GradAustralia publish **no** public feed, so they can't be added directly — but their roles are caught through the graduate/intern search terms, which also hit Seek/Indeed/company pages.)
- **Update your resume** → edit `PROFILE_DS` / `PROFILE_QA` in `profile.py`.
- **Fewer emails, only great fits** → raise `MIN_FIT_EMAIL` in `config.py`.
- **Cut cost ~3×** → set `MODEL=claude-haiku-4-5` (slightly less polished cover letters).
- **More/less volume** → `MAX_NEW_JOBS` caps how many jobs Claude scores per night (this is your main cost lever).
- **Tailored resumes** → `TAILOR_FIT` (min fit % to get one, default 65) and `MAX_TAILORED` (max per night, default 8). Attachments arrive as plain-text; paste into your Word template before submitting, and always give it a 30-second sanity read.

## Roughly what it costs

Claude is the only paid piece. At the default (Sonnet, ≤20 new jobs/night) it's typically **well under AUD $1/day**, often a few cents on quiet days. Haiku cuts that further. Everything else is free tier.

## Pair it with the dashboard

The `job command center` HTML dashboard is the manual companion: paste a one-off job, get instant scoring + cover letter, and track your pipeline (Saved → Applied → Interview → Offer). Same Claude prompt under the hood.

---

*Built for Satish. Stay un-bannable, apply tailored, get interviews.*
