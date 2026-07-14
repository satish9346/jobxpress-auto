"""
Claude scores each job against both profiles and writes a tailored
cover letter for strong matches. Uses the official Anthropic SDK.
"""
import json
import anthropic
import config
from profile import PROFILE_DS, PROFILE_QA

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _prompt(job, want_cover):
    cover_clause = (
        '"cover_letter": "tailored 230-300 word first-person cover letter as Satish, '
        'Australian tone, references real projects/metrics, ready to send"'
        if want_cover else '"cover_letter": ""'
    )
    return f"""You are a senior Australian tech recruiter. Compare the candidate to a job.
The candidate has TWO profiles — pick whichever fits best.

DATA SCIENCE PROFILE:
{PROFILE_DS}

QA / AUTOMATION PROFILE:
{PROFILE_QA}

Return ONLY raw JSON (no markdown) of this exact shape:
{{
 "fit_score": <integer 0-100, honest>,
 "recommended_profile": "Data Science" | "QA",
 "category": "Internship" | "Graduate program" | "Job",
 "verdict": "Strong match" | "Worth applying" | "Stretch" | "Skip",
 "reasons": [up to 3 short reasons tied to the candidate's real experience],
 "gaps": [up to 2 short honest gaps],
 {cover_clause}
}}
For "category": Internship = intern/placement role; Graduate program = structured grad program or graduate intake; otherwise Job.

--- JOB ---
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description:
{job['desc']}"""


def _call(job, want_cover):
    msg = client.messages.create(
        model=config.MODEL,
        max_tokens=1400 if want_cover else 500,
        messages=[{"role": "user", "content": _prompt(job, want_cover)}],
    )
    txt = "".join(b.text for b in msg.content if b.type == "text")
    txt = txt.replace("```json", "").replace("```", "").strip()
    s, e = txt.find("{"), txt.rfind("}")
    return json.loads(txt[s:e + 1])


def score(job):
    """Two-pass to save tokens: cheap score first, cover letter only if it clears the bar."""
    try:
        a = _call(job, want_cover=False)
    except Exception as e:
        print(f"  [score] {job['title'][:40]} failed: {e}")
        return None
    a.setdefault("category", "Job")
    if a.get("fit_score", 0) >= config.COVER_FIT:
        try:
            a2 = _call(job, want_cover=True)
            a["cover_letter"] = a2.get("cover_letter", "")
        except Exception as e:
            print(f"  [cover] {job['title'][:40]} failed: {e}")
            a["cover_letter"] = ""
    else:
        a["cover_letter"] = ""
    return a


def tailor_resume(job, analysis):
    """
    Rewrites the chosen base resume to mirror THIS job description:
    summary line, skill ordering, bullet emphasis. Facts stay 100% true —
    nothing invented, nothing exaggerated. Returns plain-text resume.
    """
    base = PROFILE_DS if analysis.get("recommended_profile") == "Data Science" else PROFILE_QA
    prompt = f"""You are an expert Australian resume writer. Tailor the candidate's resume to the job below.

STRICT RULES:
- Use ONLY facts from the base resume. Never invent skills, employers, dates, or metrics.
- Rewrite the professional summary to mirror the job title and its top requirements.
- Reorder skills so the job's keywords appear first (ATS-friendly, only if the candidate truly has them).
- Re-emphasise the experience bullets most relevant to this job; trim the least relevant.
- Keep it one page worth of text, plain text (no markdown), Australian English.
- Header: name, phone +61 485 511 607, email gsatishreddy2001@gmail.com, Adelaide SA, LinkedIn.

BASE RESUME:
{base}

--- JOB ---
Title: {job['title']}
Company: {job['company']}
Description:
{job['desc']}

Return ONLY the tailored resume text, nothing else."""
    try:
        msg = client.messages.create(
            model=config.MODEL,
            max_tokens=1600,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if b.type == "text").strip()
    except Exception as e:
        print(f"  [tailor] {job['title'][:40]} failed: {e}")
        return ""
