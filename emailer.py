"""
Builds the daily HTML briefing and sends it via Resend.
"""
from datetime import datetime
import requests
import config
from profile import CANDIDATE

ROUTE_COLOR = {"Data Science": "#6B4FD6", "QA": "#1A7BC0"}
VERDICT_COLOR = {
    "Strong match": "#0E9F6E", "Worth applying": "#1F4FE0",
    "Stretch": "#D9810C", "Skip": "#CF3F3F",
}


def _job_block(j):
    a = j["analysis"]
    fit = a.get("fit_score", 0)
    route = a.get("recommended_profile", "Data Science")
    verdict = a.get("verdict", "")
    rc = ROUTE_COLOR.get(route, "#1F4FE0")
    vc = VERDICT_COLOR.get(verdict, "#1F4FE0")
    reasons = "".join(
        f'<li style="margin:2px 0;color:#3D4B61;font-size:13px">{r}</li>'
        for r in a.get("reasons", [])
    )
    gaps = ""
    if a.get("gaps"):
        gaps = '<div style="font-size:12px;color:#9c5c06;margin-top:6px">Watch: ' + \
               "; ".join(a["gaps"]) + "</div>"
    cover = ""
    if a.get("cover_letter"):
        cover = (
            '<details style="margin-top:10px">'
            '<summary style="cursor:pointer;font-size:12px;font-weight:600;color:#1F4FE0">'
            'Show ready-to-send cover letter</summary>'
            f'<div style="white-space:pre-wrap;font-size:13px;line-height:1.6;color:#111A28;'
            f'background:#F4F7FB;border-radius:10px;padding:14px;margin-top:8px">'
            f'{a["cover_letter"]}</div></details>'
        )
    apply_btn = (
        f'<a href="{j["link"]}" style="display:inline-block;background:#1F4FE0;color:#fff;'
        f'text-decoration:none;font-size:13px;font-weight:600;padding:8px 16px;border-radius:8px">'
        f'Apply &rarr;</a>' if j.get("link") else ""
    )
    resume_note = ""
    if j.get("tailored_resume"):
        resume_note = (
            '<div style="font-size:12px;font-weight:700;color:#0E9F6E;margin-top:8px">'
            f'📎 Tailored resume attached: {_att_name(j)}</div>'
        )
    return f"""
    <div style="border:1px solid #D7DEE7;border-radius:14px;padding:18px 20px;margin-bottom:14px;background:#fff">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
        <span style="font-family:monospace;font-weight:700;font-size:20px;color:{vc}">{fit}%</span>
        <span style="font-size:11px;font-weight:700;color:{rc};background:{rc}18;padding:2px 8px;border-radius:6px">{route} resume</span>
        <span style="font-size:11px;font-weight:600;color:{vc}">{verdict}</span>
      </div>
      <div style="font-size:16px;font-weight:700;color:#111A28">{j['title']}</div>
      <div style="font-size:13px;color:#6B788C;margin-bottom:8px">{j['company'] or '—'} &middot; {j['location'] or ''} &middot; via {j['source']}</div>
      <ul style="margin:6px 0 0;padding-left:18px">{reasons}</ul>
      {gaps}
      <div style="margin-top:12px">{apply_btn}</div>
      {resume_note}
      {cover}
    </div>"""


def _att_name(j):
    """Safe filename for a tailored resume attachment."""
    import re
    co = re.sub(r"[^A-Za-z0-9]+", "_", (j.get("company") or "role"))[:24].strip("_") or "role"
    return f"Satish_Resume_{co}.txt"


CATEGORY_ORDER = ["Internship", "Graduate program", "Job"]
CATEGORY_ICON = {"Internship": "🎓", "Graduate program": "🚀", "Job": "💼"}


def build_html(matches, stats):
    date = datetime.now().strftime("%A, %d %B %Y")
    sections = []
    for cat in CATEGORY_ORDER:
        group = [j for j in matches if j["analysis"].get("category", "Job") == cat]
        if not group:
            continue
        sections.append(
            f'<div style="font-size:13px;font-weight:800;letter-spacing:1px;color:#3D4B61;'
            f'margin:22px 0 10px;text-transform:uppercase">{CATEGORY_ICON[cat]} {cat}s '
            f'<span style="color:#6B788C;font-weight:600">({len(group)})</span></div>'
        )
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
        You click apply — that keeps your accounts safe. Tune thresholds in config.py.
      </div>
    </div>"""


def send(matches, stats):
    import base64
    html = build_html(matches, stats)
    subject = f"{stats['new']} new job matches — {datetime.now().strftime('%d %b')}"

    # attach tailored resumes (Resend: base64 content + filename)
    attachments, used = [], set()
    for j in matches:
        txt = j.get("tailored_resume")
        if not txt:
            continue
        name = _att_name(j)
        # avoid duplicate filenames if two roles share a company
        base = name
        n = 2
        while name in used:
            name = base.replace(".txt", f"_{n}.txt")
            n += 1
        used.add(name)
        attachments.append({
            "filename": name,
            "content": base64.b64encode(txt.encode("utf-8")).decode("ascii"),
        })

    payload = {
        "from": config.EMAIL_FROM,
        "to": [CANDIDATE["email"]],
        "subject": subject,
        "html": html,
    }
    if attachments:
        payload["attachments"] = attachments

    r = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {config.RESEND_API_KEY}"},
        json=payload,
        timeout=60,
    )
    if r.status_code >= 300:
        print(f"  [email] Resend error {r.status_code}: {r.text}")
        return False
    print("  email sent ✓")
    return True
