"""
Builds the daily HTML briefing and sends it via Resend.
Attaches a tailored resume AND cover letter as PDFs for strong matches,
and gives each job a direct "company careers" search link (better ATS pickup
than aggregator redirects).
"""
import re
import base64
from datetime import datetime
from urllib.parse import quote_plus
import requests
import config
import docgen
from profile import CANDIDATE

ROUTE_COLOR = {"Data Science": "#6B4FD6", "QA": "#1A7BC0"}
VERDICT_COLOR = {"Strong match": "#0E9F6E", "Worth applying": "#1F4FE0",
                 "Stretch": "#D9810C", "Skip": "#CF3F3F"}

# order sections so student-friendly ones sit at the top
CATEGORY_ORDER = ["Vacation program", "Internship", "Graduate program",
                  "Part-time", "Casual", "Job"]
CATEGORY_ICON = {"Vacation program": "🌟", "Internship": "🎓",
                 "Graduate program": "🚀", "Part-time": "🕒",
                 "Casual": "🗓️", "Job": "💼"}


def _slug(j):
    return re.sub(r"[^A-Za-z0-9]+", "_", (j.get("company") or "role"))[:24].strip("_") or "role"

def _careers_link(j):
    q = quote_plus(f'{j.get("company","")} careers {j.get("title","")}')
    return f"https://www.google.com/search?q={q}"


def _job_block(j):
    a = j["analysis"]
    fit = a.get("fit_score", 0)
    route = a.get("recommended_profile", "Data Science")
    verdict = a.get("verdict", "")
    rc = ROUTE_COLOR.get(route, "#1F4FE0")
    vc = VERDICT_COLOR.get(verdict, "#1F4FE0")
    pri = a.get("student_priority")
    pri_badge = ('<span style="font-size:10px;font-weight:700;color:#0E9F6E;'
                 'background:#E4F6EF;padding:2px 8px;border-radius:6px">★ STUDENT-FRIENDLY</span>') if pri else ""
    reasons = "".join(f'<li style="margin:2px 0;color:#3D4B61;font-size:13px">{r}</li>'
                      for r in a.get("reasons", []))
    gaps = ""
    if a.get("gaps"):
        gaps = ('<div style="font-size:12px;color:#9c5c06;margin-top:6px">Watch: '
                + "; ".join(a["gaps"]) + "</div>")
    cover = ""
    pack = j.get("pack")
    if pack:
        a["cover_letter"] = "\n\n".join(v for v in pack["cover"].values() if v)
    if a.get("cover_letter"):
        cover = ('<details style="margin-top:10px">'
                 '<summary style="cursor:pointer;font-size:12px;font-weight:600;color:#1F4FE0">'
                 'Show cover letter text</summary>'
                 f'<div style="white-space:pre-wrap;font-size:13px;line-height:1.6;color:#111A28;'
                 f'background:#F4F7FB;border-radius:10px;padding:14px;margin-top:8px">'
                 f'{a["cover_letter"]}</div></details>')
    apply_btn = (f'<a href="{j["link"]}" style="display:inline-block;background:#1F4FE0;color:#fff;'
                 f'text-decoration:none;font-size:13px;font-weight:600;padding:8px 16px;border-radius:8px">'
                 f'Apply via link &rarr;</a>' if j.get("link") else "")
    careers_btn = (f'<a href="{_careers_link(j)}" style="display:inline-block;margin-left:8px;'
                   f'background:#fff;border:1px solid #1F4FE0;color:#1F4FE0;text-decoration:none;'
                   f'font-size:13px;font-weight:600;padding:7px 14px;border-radius:8px">'
                   f'Find on company site ↗</a>')
    files_note = ""
    if j.get("files"):
        k = pack["keywords"]
        kc = "#0E9F6E" if k["coverage"] >= 70 else "#D9810C"
        add = (f'<div style="color:#3D4B61">Add if true: {", ".join(k["could_add"])}</div>' if k["could_add"] else "")
        gap = (f'<div style="color:#9c5c06">Real gaps: {", ".join(k["gaps"])}</div>' if k["gaps"] else "")
        fixed = (f'<div style="color:#6B788C">Fact check repaired {len(pack["problems"])} item(s)</div>'
                 if pack["problems"] else '<div style="color:#6B788C">Fact check: all claims match your facts file</div>')
        files_note = (f'<div style="font-size:12px;margin-top:10px;line-height:1.6">'
                      f'<div style="font-weight:700;color:#0E9F6E">📎 Attached: {", ".join(j["files"])}</div>'
                      f'<div style="font-weight:700;color:{kc}">ATS keyword match: {k["coverage"]}% '
                      f'({len(k["matched"])} of {len(pack["job_keywords"])} keywords from the ad)</div>'
                      f'{add}{gap}{fixed}'
                      f'<div style="color:#6B788C">Read both before sending. Edit the .docx if anything is off.</div></div>')
    return f"""
    <div style="border:1px solid #D7DEE7;border-radius:14px;padding:18px 20px;margin-bottom:14px;background:#fff">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap">
        <span style="font-family:monospace;font-weight:700;font-size:20px;color:{vc}">{fit}%</span>
        <span style="font-size:11px;font-weight:700;color:{rc};background:{rc}18;padding:2px 8px;border-radius:6px">{route} resume</span>
        <span style="font-size:11px;font-weight:600;color:{vc}">{verdict}</span>
        {pri_badge}
      </div>
      <div style="font-size:16px;font-weight:700;color:#111A28">{j['title']}</div>
      <div style="font-size:13px;color:#6B788C;margin-bottom:8px">{j['company'] or '—'} &middot; {j['location'] or ''} &middot; via {j['source']}</div>
      <ul style="margin:6px 0 0;padding-left:18px">{reasons}</ul>
      {gaps}
      <div style="margin-top:12px">{apply_btn}{careers_btn}</div>
      {files_note}
      {cover}
    </div>"""


def build_html(matches, stats):
    date = datetime.now().strftime("%A, %d %B %Y")
    sections = []
    for cat in CATEGORY_ORDER:
        group = [j for j in matches if j["analysis"].get("category", "Job") == cat]
        if not group:
            continue
        icon = CATEGORY_ICON.get(cat, "💼")
        sections.append(
            f'<div style="font-size:13px;font-weight:800;letter-spacing:1px;color:#3D4B61;'
            f'margin:22px 0 10px;text-transform:uppercase">{icon} {cat} '
            f'<span style="color:#6B788C;font-weight:600">({len(group)})</span></div>')
        sections.extend(_job_block(j) for j in group)
    blocks = "".join(sections) or \
        '<div style="padding:20px;color:#6B788C">No new roles above your fit threshold today. Tomorrow’s a fresh pull.</div>'
    return f"""
    <div style="max-width:640px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#E7EBF0;padding:24px">
      <div style="background:#141E30;border-radius:16px;padding:24px;color:#fff;margin-bottom:18px">
        <div style="font-size:11px;letter-spacing:1.5px;color:#8FA3C4;font-weight:700">JOBXPRESS · DAILY BRIEFING</div>
        <div style="font-size:13px;color:#9DB0CE;margin-top:4px">{date}</div>
        <div style="display:flex;gap:28px;margin-top:18px">
          <div><div style="font-size:26px;font-weight:700">{stats['new']}</div><div style="font-size:11px;color:#9DB0CE">NEW MATCHES</div></div>
          <div><div style="font-size:26px;font-weight:700;color:#6FE3B4">{stats['top']}</div><div style="font-size:11px;color:#9DB0CE">STRONG (75%+)</div></div>
          <div><div style="font-size:26px;font-weight:700">{stats['scanned']}</div><div style="font-size:11px;color:#9DB0CE">SCANNED</div></div>
        </div>
      </div>
      {blocks}
      <div style="text-align:center;font-size:11px;color:#6B788C;margin-top:16px">
        You click apply — that keeps your accounts safe. Every match is logged to applications.csv.
      </div>
    </div>"""


def _attach(name, data_bytes):
    return {"filename": name, "content": base64.b64encode(data_bytes).decode("ascii")}


def send_free(jobs, stats):
    """FREE MODE email — no AI. Just lists the new job postings with links."""
    date = datetime.now().strftime("%A, %d %B %Y")
    rows = []
    for j in jobs:
        apply_btn = (f'<a href="{j["link"]}" style="display:inline-block;background:#1F4FE0;color:#fff;'
                     f'text-decoration:none;font-size:12px;font-weight:600;padding:6px 13px;border-radius:7px">Apply &rarr;</a>'
                     if j.get("link") else "")
        careers = (f'<a href="{_careers_link(j)}" style="display:inline-block;margin-left:6px;background:#fff;'
                   f'border:1px solid #1F4FE0;color:#1F4FE0;text-decoration:none;font-size:12px;font-weight:600;'
                   f'padding:5px 11px;border-radius:7px">Company site ↗</a>')
        rows.append(f"""
        <div style="border:1px solid #D7DEE7;border-radius:12px;padding:14px 16px;margin-bottom:10px;background:#fff">
          <div style="font-size:15px;font-weight:700;color:#111A28">{j.get('title','')}</div>
          <div style="font-size:12.5px;color:#6B788C;margin:3px 0 9px">{j.get('company') or '—'} &middot; {j.get('location') or ''} &middot; via {j.get('source','')}</div>
          <div>{apply_btn}{careers}</div>
        </div>""")
    body = "".join(rows) or '<div style="padding:18px;color:#6B788C">No new listings today.</div>'
    html = f"""
    <div style="max-width:640px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#E7EBF0;padding:22px">
      <div style="background:#141E30;border-radius:16px;padding:22px;color:#fff;margin-bottom:16px">
        <div style="font-size:11px;letter-spacing:1.5px;color:#8FA3C4;font-weight:700">JOBXPRESS · FREE MODE · NEW LISTINGS</div>
        <div style="font-size:13px;color:#9DB0CE;margin-top:4px">{date}</div>
        <div style="display:flex;gap:26px;margin-top:16px">
          <div><div style="font-size:24px;font-weight:700">{stats['new']}</div><div style="font-size:11px;color:#9DB0CE">NEW LISTINGS</div></div>
          <div><div style="font-size:24px;font-weight:700">{stats['scanned']}</div><div style="font-size:11px;color:#9DB0CE">SCANNED</div></div>
        </div>
      </div>
      {body}
      <div style="text-align:center;font-size:11px;color:#6B788C;margin-top:14px">
        Free mode: raw listings, no AI scoring. Paste any into your dashboard for a fit score + cover letter.
      </div>
    </div>"""
    subject = f"{stats['new']} new job listings — {datetime.now().strftime('%d %b')} (free mode)"
    r = requests.post("https://api.resend.com/emails",
                      headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
                      json={"from": config.EMAIL_FROM, "to": [CANDIDATE["email"]],
                            "subject": subject, "html": html}, timeout=60)
    if r.status_code >= 300:
        print(f"  [email] Resend error {r.status_code}: {r.text}")
        return False
    print("  free-mode email sent ✓")
    return True


def send(matches, stats):
    # build PDFs first (also sets *_pdf_name on each job so the email can note them)
    attachments, used = [], set()

    def uniq(name):
        base, n = name, 2
        while name in used:
            stem, ext = base.rsplit(".", 1)
            name = f"{stem}_{n}.{ext}"
            n += 1
        used.add(name)
        return name

    for j in matches:
        if not j.get("pack"):
            continue
        try:
            files = docgen.render_all(j["pack"])
        except Exception as ex:
            print(f"  [docs] {j['title'][:30]} failed: {ex}")
            continue
        j["files"] = []
        for name, data in files.items():
            name = uniq(name)
            attachments.append(_attach(name, data))
            j["files"].append(name)

    html = build_html(matches, stats)
    subject = f"{stats['new']} new job matches — {datetime.now().strftime('%d %b')}"
    payload = {"from": config.EMAIL_FROM, "to": [CANDIDATE["email"]],
               "subject": subject, "html": html}
    if attachments:
        payload["attachments"] = attachments

    r = requests.post("https://api.resend.com/emails",
                      headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
                      json=payload, timeout=90)
    if r.status_code >= 300:
        print(f"  [email] Resend error {r.status_code}: {r.text}")
        return False
    print(f"  email sent ✓ ({len(attachments)} attachments)")
    return True
