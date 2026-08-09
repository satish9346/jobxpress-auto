# JobXpress — your automatic job-finding pipeline

Every night this:
1. **Finds** fresh Data Science + QA roles across Australia (Adzuna + Jooble APIs — legal aggregators covering Seek, Indeed, LinkedIn & thousands of company career pages, plus any RSS feeds you add).
2. **Scores** each with Claude against your two resumes (DS and QA), picks the better-fit resume, flags gaps, and classifies it as **Internship / Graduate program / Job**.
3. **Writes** a ready-to-send cover letter for strong matches.
4. **Tailors your resume per job** for the top matches — summary, skill order and bullet emphasis rewritten to mirror that job's description (facts never invented) — attached to the email as `Satish_Resume_<Company>.txt`.
5. **Emails** you one briefing, grouped Internships → Graduate programs → Jobs, each with fit %, reasons, gaps, Apply link, cover letter, and tailored resume attached.

You wake up, open the email, click **Apply** on the best few. The clicking stays with you — that's deliberate. Bots that auto-submit get Seek/LinkedIn/Indeed accounts **banned**, and auto-filled applications get auto-rejected. This tool kills the slow 90% (searching, matching, writing) and keeps you safe and in control.

No passwords for any job board are ever used or needed.

---


## What's new in this version
- **PDF attachments** — tailored resume AND cover letter arrive as clean, ATS-friendly PDFs (still read each one before sending — you're accountable for every word).
- **Application tracker** — every emailed match is appended to `applications.csv` in the repo. Open it in Excel; update the `status` column yourself (Applied / Interview / Rejected / Offer). It grows over time.
- **"Find on company site" link** — each job gets a Google link to the company's own careers page, which usually gives better ATS pickup than aggregator redirects.
- **Student-priority ranking** — part-time, casual, internships, vacation programs and graduate programs are flagged and sorted to the top of the email.

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
