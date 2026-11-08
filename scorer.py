"""
Claude scores each job against both career tracks (data and QA), built from facts.py.
Writing resumes and cover letters is done by resume_agent.py, for top matches only.
"""
import json

import anthropic

import config
import facts

client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None


def _prompt(job):
    return f"""You are a senior Australian tech recruiter screening for one candidate. Be honest and strict.

DATA TRACK PROFILE:
{facts.profile_text("data")}

QA TRACK PROFILE:
{facts.profile_text("qa")}

Rules:
- The candidate is in Adelaide on a student visa (full work rights expected mid 2027). Jobs outside Australia score 0, verdict "Skip".
- Roles that require Australian citizenship, permanent residency or a security clearance score below 20, verdict "Skip".
- Roles needing 4+ years or senior/lead/manager level score below 35.
- Graduate, junior, internship and entry-level data, BI, reporting or QA roles in Adelaide or remote Australia score highest.

Return ONLY raw JSON (no markdown):
{{
 "fit_score": <integer 0-100>,
 "recommended_profile": "Data Science" | "QA",
 "category": "Internship" | "Graduate program" | "Part-time" | "Casual" | "Vacation program" | "Job",
 "student_priority": true | false,
 "verdict": "Strong match" | "Worth applying" | "Stretch" | "Skip",
 "reasons": [up to 3 short reasons tied to the candidate's real experience],
 "gaps": [up to 2 short honest gaps]
}}
"category": Internship = intern/placement; Graduate program = structured grad intake; Part-time / Casual = explicitly part-time or casual hours; Vacation program = summer/vacationer program; otherwise Job.
"student_priority": true for part-time, casual, internship, vacation or graduate programs.

--- JOB ---
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description:
{job['desc']}"""


def score(job):
    try:
        msg = client.messages.create(model=config.MODEL, max_tokens=500,
                                     messages=[{"role": "user", "content": _prompt(job)}])
        txt = "".join(b.text for b in msg.content if b.type == "text")
        txt = txt.replace("```json", "").replace("```", "").strip()
        a = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
    except Exception as e:
        print(f"  [score] {job['title'][:40]} failed: {e}")
        return None
    a.setdefault("category", "Job")
    a.setdefault("student_priority", False)
    a["fit_score"] = max(0, min(100, int(a.get("fit_score", 0))))
    a["cover_letter"] = ""   # written by resume_agent for top matches
    return a
