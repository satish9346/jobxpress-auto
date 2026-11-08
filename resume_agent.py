"""
Resume Tailor agent.

For one job it:
  1. reads the job description and pulls out the exact keywords and requirements,
  2. builds a tailored resume and cover letter from facts.py only,
  3. checks every number, skill and bullet against facts.py and repairs anything invented,
  4. scores keyword coverage the way an ATS would (exact phrase match),
  5. returns a structured "pack" that docgen.py turns into DOCX and PDF files.

Why this design (from research, Nov 2026):
  - Tailored resumes convert to interviews about 2x more often than generic ones.
  - Australian recruiters expect: single column, no photo or birth date, contact
    details in the body, a work-rights line, 2 pages, Australian spelling, and the
    ad's own wording in the title, summary and skills.
  - AI resume tools are useful but invent facts if unchecked, so every claim here
    is verified in code, not trusted to the model.
"""
import json
import re

import config
import facts

BANNED = [
    (r"\bg'?day\b", "casual greeting"), (r"\bcheers\b", "casual sign-off"),
    (r"visa sponsorship|sponsor(ship)? .*visa|h-?1b", "visa sponsorship talk"),
    (r"\brelocat", "relocation talk"), (r"software engineer at cognizant", "wrong job title"),
    (r"\bpassionate\b", "cliche"), (r"\bsurgical precision\b", "cliche"),
    (r"\b(i am|i'm) (a |the )?perfect\b", "overclaim"),
]

PROMPT = """You are an expert Australian resume writer and recruiter. Tailor the candidate's application to ONE job.

HARD RULES (code will check these and undo any breach):
- Use ONLY the facts below. Never add an employer, title, date, number, tool, certificate or degree.
- Every number you write must already appear in the facts, exactly.
- Choose bullets by their id. You may reword a bullet to mirror the ad's language, but keep its numbers and meaning.
- Skills must come from the SKILLS list, written exactly as listed. Put the ad's keywords first, only if the candidate has them.
- Australian English (analyse, optimise, organisation). Professional, warm, plain. No "G'day", no "Cheers", no clichés like "passionate".
- Do not mention visa sponsorship or relocation. The resume already states work rights.
- Experience length: {months} months in industry. Never write a different figure.

CANDIDATE FACTS
Headline options, data track: {h_data}
Headline options, QA track: {h_qa}
{profile}

BULLETS (id: text)
{bullets}

PROJECTS (id: name: text)
{projects}

SKILLS
{skills}

JOB
Title: {title}
Company: {company}
Location: {location}
Description:
{desc}

Return ONLY raw JSON, no markdown:
{{
 "track": "data" | "qa",
 "job_keywords": [8 to 20 exact words or short phrases from the ad that an ATS would match: tools, skills, methods, domain terms],
 "must_haves": [up to 6 key requirements in plain words],
 "requires_citizenship_or_clearance": true | false,
 "headline": one of the headline options above, the closest to the job title,
 "summary": "3 to 4 sentences, under 80 words. Open with the headline and {months} months of industry experience at Cognizant on insurance and financial services clients. Mirror the ad's top requirements. End with what the candidate is looking for.",
 "skills": [10 to 16 skills from the SKILLS list, most relevant first],
 "experience": [{{"id": "bullet id", "text": "reworded bullet"}}, ... 4 to 6 bullets from Cognizant, most relevant first],
 "include_woolworths": true | false,
 "projects": [{{"id": "project id", "text": "reworded one-line description"}}, ... 2 to 3 projects most relevant to this job],
 "cover_letter": {{
    "opening": "2 sentences: the exact role and company, and the single strongest reason the candidate fits.",
    "evidence": "3 to 4 sentences linking 2 or 3 of the job's must-haves to specific facts with their numbers.",
    "company": "1 to 2 sentences on why this company or team, using only what the job ad says about them.",
    "close": "1 to 2 sentences: availability, work rights in brief, and a polite request for an interview."
 }}
}}"""


def _bullet_lines():
    return "\n".join(f"{b['id']}: [{job['employer']}{' / ' + b['client'] if b['client'] else ''}] {b['text']}"
                     for job in facts.EXPERIENCE for b in job["bullets"])


def _project_lines():
    return "\n".join(f"{p['id']}: {p['name']}: {p['text']}" for p in facts.PROJECTS)


def _skill_lines():
    return "\n".join(f"{k}: {', '.join(v)}" for k, v in facts.SKILLS.items())


NUM = re.compile(r"\d[\d,]*(?:\.\d+)?%?\+?")


def _numbers(text):
    """Normalised numbers in a text: '50,000+' -> '50000', '98.4%' -> '98.4'."""
    out = set()
    for m in NUM.findall(text or ""):
        n = m.replace(",", "").rstrip("+%")
        if n:
            out.add(n.rstrip(".") if "." in n else n)
    return out


FACT_NUMBERS = None


def _fact_numbers():
    global FACT_NUMBERS
    if FACT_NUMBERS is None:
        FACT_NUMBERS = _numbers(facts.corpus()) | {str(facts.tech_months()), "2", "3", "10"}
    return FACT_NUMBERS


STOP = set("a an the and or of to in on for with by at from as is are was were be been this that these those "
           "my i me we our your their its it into across all over more than per using used".split())


def _words(text):
    return {w for w in re.findall(r"[a-z]+", (text or "").lower()) if w not in STOP and len(w) > 2}


FACT_SENTENCES = None


def _fact_sentences():
    global FACT_SENTENCES
    if FACT_SENTENCES is None:
        FACT_SENTENCES = [s for s in re.split(r"(?<=[.!?])\s+|\n", facts.corpus()) if s.strip()]
    return FACT_SENTENCES


def _unsupported_numbers(sentence):
    """Numbers whose claim is not backed by a fact sentence with the same number and related words."""
    bad = set()
    words = _words(sentence)
    for n in _numbers(sentence):
        if n in (str(facts.tech_months()), "2", "3"):
            continue
        backing = [f for f in _fact_sentences() if n in _numbers(f)]
        if not any(len(words & _words(f)) >= 2 for f in backing):
            bad.add(n)
    return bad


def _fix_experience_length(text):
    """Replace rounded-up claims like 'two years' with the exact months from facts.py."""
    m = facts.tech_months()
    return re.sub(r"\b(two|2|over two|nearly two|almost two)\+?\s+years'?(\s+of)?", f"{m} months\\2", text or "",
                  flags=re.I)


def _strip_bad_sentences(text, problems, where):
    """Remove sentences that contain invented numbers or banned phrases."""
    keep = []
    for s in re.split(r"(?<=[.!?])\s+", _fix_experience_length(text).strip()):
        bad_nums = _unsupported_numbers(s)
        bad_phrase = next((label for pat, label in BANNED if re.search(pat, s, re.I)), None)
        if bad_nums:
            problems.append(f"{where}: removed a sentence with unverified number(s) {sorted(bad_nums)}")
        elif bad_phrase:
            problems.append(f"{where}: removed a sentence ({bad_phrase})")
        else:
            keep.append(s)
    return " ".join(keep)


def verify(draft):
    """Repair the model's draft so every claim traces back to facts.py. Returns (pack, problems)."""
    problems = []
    bullets = facts.all_bullets()
    skills = facts.all_skills()

    track = draft.get("track") if draft.get("track") in ("data", "qa") else "data"
    headline = draft.get("headline", "")
    if headline not in facts.HEADLINES["data"] + facts.HEADLINES["qa"]:
        problems.append(f"headline '{headline}' not allowed, used default")
        headline = facts.HEADLINES[track][0]

    exp = []
    for item in draft.get("experience", [])[:6]:
        bid = item.get("id")
        if bid not in bullets or bullets[bid][0]["id"] != "cognizant":
            problems.append(f"experience: unknown bullet '{bid}' dropped")
            continue
        original = bullets[bid][1]["text"]
        text = (item.get("text") or "").strip() or original
        if _numbers(text) != _numbers(original) or any(re.search(p, text, re.I) for p, _ in BANNED):
            problems.append(f"experience {bid}: numbers or wording changed, original kept")
            text = original
        exp.append({"id": bid, "text": text})
    if len(exp) < 3:   # never send a thin resume
        defaults = ["m1", "m2", "m3", "v4"] if track == "data" else ["v1", "v2", "v3", "v4"]
        have = {e["id"] for e in exp}
        exp += [{"id": b, "text": bullets[b][1]["text"]} for b in defaults if b not in have]
        problems.append("experience: too few valid bullets, defaults added")

    sk, seen = [], set()
    for s in draft.get("skills", []):
        key = (s or "").lower().strip()
        if key in skills and key not in seen:
            sk.append(skills[key]); seen.add(key)
        elif key and key not in seen:
            problems.append(f"skills: '{s}' is not in facts, dropped")
    if len(sk) < 8:
        for s in facts.SKILLS["Languages"] + facts.SKILLS["Visualisation and BI"][:2] + facts.SKILLS["Testing and QA"][:2]:
            if s.lower() not in seen:
                sk.append(s); seen.add(s.lower())

    projects_by_id = {p["id"]: p for p in facts.PROJECTS}
    pr = []
    for item in draft.get("projects", [])[:3]:
        p = projects_by_id.get(item.get("id"))
        if not p:
            problems.append(f"projects: unknown '{item.get('id')}' dropped")
            continue
        text = (item.get("text") or "").strip() or p["text"]
        if not _numbers(text) <= _numbers(p["text"]):
            problems.append(f"project {p['id']}: numbers changed, original kept")
            text = p["text"]
        pr.append({"id": p["id"], "name": p["name"], "text": text, "tools": p["tools"]})

    summary = _strip_bad_sentences(draft.get("summary", ""), problems, "summary")
    cl = draft.get("cover_letter") or {}
    cover = {k: _strip_bad_sentences(cl.get(k, ""), problems, f"cover letter {k}")
             for k in ("opening", "evidence", "company", "close")}

    pack = {
        "track": track, "headline": headline, "summary": summary, "skills": sk[:16],
        "experience": exp, "include_woolworths": bool(draft.get("include_woolworths", True)),
        "projects": pr, "cover": cover,
        "job_keywords": [k for k in draft.get("job_keywords", []) if isinstance(k, str)][:20],
        "must_haves": draft.get("must_haves", [])[:6],
        "requires_citizenship_or_clearance": bool(draft.get("requires_citizenship_or_clearance")),
    }
    return pack, problems


def resume_text(pack):
    """Everything a recruiter or ATS reads on the resume, as one string."""
    parts = [pack["headline"], pack["summary"], " ".join(pack["skills"])]
    parts += [e["text"] for e in pack["experience"]]
    parts += [f"{p['name']} {p['text']} {' '.join(p['tools'])}" for p in pack["projects"]]
    parts += [f"{e['degree']} {e['detail']}" for e in facts.EDUCATION] + facts.CERTIFICATIONS
    return " ".join(parts)


def keyword_report(pack):
    """ATS-style exact keyword match: what the resume covers, what it could add, what is a real gap."""
    text = resume_text(pack).lower()
    corpus = (facts.corpus() + " " + " ".join(facts.all_skills().values())).lower()

    def has(hay, kw):
        k = re.escape(kw.lower().rstrip("s")) if len(kw) > 3 else re.escape(kw.lower())
        return re.search(r"(?<![a-z0-9])" + k + r"(?:s|es)?(?![a-z0-9])", hay) is not None

    matched, could_add, gaps = [], [], []
    for kw in pack["job_keywords"]:
        if has(text, kw):
            matched.append(kw)
        elif has(corpus, kw):
            could_add.append(kw)
        else:
            gaps.append(kw)
    total = len(pack["job_keywords"]) or 1
    return {"coverage": round(100 * len(matched) / total), "matched": matched,
            "could_add": could_add, "gaps": gaps}


def build_pack(job, client=None):
    """Main entry point. Returns a verified pack dict, or None if the model call fails."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    prompt = PROMPT.format(
        months=facts.tech_months(),
        h_data=", ".join(facts.HEADLINES["data"]), h_qa=", ".join(facts.HEADLINES["qa"]),
        profile=facts.profile_text("all"), bullets=_bullet_lines(), projects=_project_lines(),
        skills=_skill_lines(), title=job.get("title", ""), company=job.get("company", ""),
        location=job.get("location", ""), desc=(job.get("desc") or "")[:6000])
    try:
        msg = client.messages.create(model=config.WRITE_MODEL, max_tokens=2500,
                                     messages=[{"role": "user", "content": prompt}])
        txt = "".join(b.text for b in msg.content if b.type == "text")
        s, e = txt.find("{"), txt.rfind("}")
        draft = json.loads(txt[s:e + 1])
    except Exception as ex:
        print(f"  [tailor] {job.get('title', '')[:40]} failed: {ex}")
        return None
    pack, problems = verify(draft)
    pack["keywords"] = keyword_report(pack)
    pack["problems"] = problems
    pack["job"] = {k: job.get(k, "") for k in ("title", "company", "location", "link", "source")}
    return pack
