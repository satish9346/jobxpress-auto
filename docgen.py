"""
Renders a verified pack into an ATS-friendly resume and cover letter, as DOCX and PDF.

Format follows Australian recruiter and ATS guidance:
  single column, no tables, text boxes, photo or birth date; contact details in the
  page body (not the header); a work-rights line; standard section headings;
  Calibri/Helvetica; A4; up to 2 pages.
Dates, employers and titles come from facts.py, never from the model.
"""
import io
from datetime import date

import facts

ACCENT = (0x1E, 0x4E, 0x79)


def _contact_line():
    c = facts.CONTACT
    bits = [c["location"], c["phone"], c["email"], c["linkedin"], c["github"], c["portfolio"]]
    return "  |  ".join(b for b in bits if b)


def _experience_blocks(pack):
    """[(job dict, [bullet texts])] in display order."""
    blocks = []
    cog = next(j for j in facts.EXPERIENCE if j["id"] == "cognizant")
    blocks.append((cog, [e["text"] for e in pack["experience"]]))
    if pack.get("include_woolworths"):
        ww = next(j for j in facts.EXPERIENCE if j["id"] == "woolworths")
        blocks.append((ww, [b["text"] for b in ww["bullets"]]))
    return blocks


def _clients_line(pack):
    bullets = facts.all_bullets()
    clients = []
    for e in pack["experience"]:
        c = bullets[e["id"]][1]["client"]
        if c and c not in clients:
            clients.append(c)
    names = {"MetLife": "MetLife (insurance)", "VOYA": "VOYA (financial services)"}
    return "Clients: " + ", ".join(names.get(c, c) for c in clients) if clients else ""


# ---------------------------------------------------------------- DOCX
def resume_docx(pack):
    from docx import Document
    from docx.enum.text import WD_TAB_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt, RGBColor

    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Mm(297), Mm(210)
    sec.left_margin = sec.right_margin = Mm(17)
    sec.top_margin = sec.bottom_margin = Mm(14)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Calibri", Pt(10.5)
    normal.paragraph_format.space_after = Pt(2)

    def para(text="", size=10.5, bold=False, italic=False, color=None, after=2, before=0):
        p = doc.add_paragraph()
        p.paragraph_format.space_after, p.paragraph_format.space_before = Pt(after), Pt(before)
        if text:
            r = p.add_run(text)
            r.font.size, r.bold, r.italic = Pt(size), bold, italic
            if color:
                r.font.color.rgb = RGBColor(*color)
        return p

    def heading(text):
        p = para(text.upper(), size=11, bold=True, color=ACCENT, after=3, before=8)
        p.paragraph_format.keep_with_next = True
        pPr = p._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", "1E4E79")):
            bottom.set(qn(k), v)
        bdr.append(bottom)
        pPr.append(bdr)

    def bullet(text):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(1.5)
        p.add_run(text).font.size = Pt(10.5)

    def role_line(left, right):
        p = para(after=0, before=4)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.tab_stops.add_tab_stop(sec.page_width - sec.left_margin - sec.right_margin,
                                                  WD_TAB_ALIGNMENT.RIGHT)
        r = p.add_run(left); r.bold = True; r.font.size = Pt(11)
        r2 = p.add_run("\t" + right); r2.font.size = Pt(10)

    para(facts.CONTACT["name"], size=20, bold=True, after=0)
    para(pack["headline"], size=12, bold=True, color=ACCENT, after=1)
    para(_contact_line(), size=9.5, after=1)
    para("Work rights: " + facts.WORK_RIGHTS, size=9.5, italic=True, after=2)

    heading("Professional Summary")
    para(pack["summary"])

    heading("Key Skills")
    para("  •  ".join(pack["skills"]))

    heading("Professional Experience")
    for job, items in _experience_blocks(pack):
        role_line(f"{job['title']}, {job['employer']}", f"{job['dates']}  |  {job['location']}")
        if job["id"] == "cognizant" and _clients_line(pack):
            para(_clients_line(pack), size=10, italic=True, after=1)
        for t in items:
            bullet(t)

    if pack["projects"]:
        heading("Projects")
        for p in pack["projects"]:
            q = para(after=1, before=2)
            r = q.add_run(p["name"] + ": "); r.bold = True
            q.add_run(p["text"] + f" ({', '.join(p['tools'])})")

    heading("Education")
    for e in facts.EDUCATION:
        role_line(f"{e['degree']}, {e['school']}", e["dates"])
        para(e["detail"], size=10, italic=True, after=1)

    heading("Certifications")
    para("  •  ".join(facts.CERTIFICATIONS + facts.IN_PROGRESS))

    heading("Additional")
    para("Languages: " + ", ".join(facts.LANGUAGES) + ".   Referees: available on request.")
    return _save_docx(doc)


def cover_docx(pack):
    from docx import Document
    from docx.shared import Mm, Pt

    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Mm(297), Mm(210)
    sec.left_margin = sec.right_margin = Mm(22)
    sec.top_margin = sec.bottom_margin = Mm(20)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)
    for text, kw in _cover_lines(pack):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(kw.get("after", 8))
        r = p.add_run(text)
        r.bold = kw.get("bold", False)
        r.font.size = Pt(kw.get("size", 11))
    return _save_docx(doc)


def _save_docx(doc):
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _cover_lines(pack):
    j, c = pack["job"], pack["cover"]
    company = j.get("company") or "the hiring team"
    lines = [
        (facts.CONTACT["name"], {"bold": True, "size": 14, "after": 0}),
        (_contact_line(), {"size": 9.5, "after": 12}),
        (date.today().strftime("%d %B %Y").lstrip("0"), {"after": 12}),
        (f"Re: {j.get('title', 'the advertised role')}", {"bold": True, "after": 12}),
        (f"Dear Hiring Manager,", {"after": 10}),
    ]
    for key in ("opening", "evidence", "company", "close"):
        if c.get(key):
            lines.append((c[key], {"after": 10}))
    lines += [("Kind regards,", {"after": 2}), (facts.CONTACT["name"], {"bold": True, "after": 0})]
    return lines


# ---------------------------------------------------------------- PDF
def _pdf_styles():
    from reportlab.lib.colors import Color
    from reportlab.lib.styles import ParagraphStyle
    acc = Color(*(v / 255 for v in ACCENT))
    base = ParagraphStyle("b", fontName="Helvetica", fontSize=9.6, leading=13)
    return {
        "body": base,
        "name": ParagraphStyle("n", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22),
        "head": ParagraphStyle("h", parent=base, fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=acc),
        "small": ParagraphStyle("s", parent=base, fontSize=8.8, leading=11.5),
        "ital": ParagraphStyle("i", parent=base, fontName="Helvetica-Oblique", fontSize=9, leading=12),
        "sec": ParagraphStyle("x", parent=base, fontName="Helvetica-Bold", fontSize=10, leading=13,
                              textColor=acc, spaceBefore=7, spaceAfter=2),
        "bul": ParagraphStyle("u", parent=base, leftIndent=11, bulletIndent=2, spaceAfter=1),
        "letter": ParagraphStyle("l", parent=base, fontSize=10.5, leading=15, spaceAfter=8),
    }


def _e(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def resume_pdf(pack):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

    S = _pdf_styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm,
                            topMargin=13 * mm, bottomMargin=13 * mm,
                            title=f"{facts.CONTACT['name']} - Resume", author=facts.CONTACT["name"])

    f = [Paragraph(_e(facts.CONTACT["name"]), S["name"]), Paragraph(_e(pack["headline"]), S["head"]),
         Spacer(1, 2), Paragraph(_e(_contact_line()), S["small"]),
         Paragraph(_e("Work rights: " + facts.WORK_RIGHTS), S["ital"])]

    def sec(t):
        f.append(Paragraph(t.upper(), S["sec"]))
        f.append(HRFlowable(width="100%", thickness=0.6, color=S["sec"].textColor, spaceAfter=3))

    def row(left, right):
        # plain text line (no tables), so every ATS reads it in order
        return Paragraph(f"<b>{_e(left)}</b>&nbsp;&nbsp;|&nbsp;&nbsp;{_e(right)}", S["body"])

    sec("Professional Summary"); f.append(Paragraph(_e(pack["summary"]), S["body"]))
    sec("Key Skills"); f.append(Paragraph(_e("  •  ".join(pack["skills"])), S["body"]))
    sec("Professional Experience")
    for job, items in _experience_blocks(pack):
        block = [row(f"{job['title']}, {job['employer']}", f"{job['dates']}  |  {job['location']}")]
        if job["id"] == "cognizant" and _clients_line(pack):
            block.append(Paragraph(_e(_clients_line(pack)), S["ital"]))
        f.append(KeepTogether(block + [Paragraph(_e(items[0]), S["bul"], bulletText="•")]))
        f += [Paragraph(_e(t), S["bul"], bulletText="•") for t in items[1:]]
    if pack["projects"]:
        sec("Projects")
        for p in pack["projects"]:
            f.append(Paragraph(f"<b>{_e(p['name'])}:</b> {_e(p['text'])} ({_e(', '.join(p['tools']))})", S["bul"],
                               bulletText="•"))
    sec("Education")
    for e in facts.EDUCATION:
        f += [row(f"{e['degree']}, {e['school']}", e["dates"]), Paragraph(_e(e["detail"]), S["ital"])]
    sec("Certifications"); f.append(Paragraph(_e("  •  ".join(facts.CERTIFICATIONS + facts.IN_PROGRESS)), S["body"]))
    sec("Additional")
    f.append(Paragraph(_e("Languages: " + ", ".join(facts.LANGUAGES) + ".   Referees: available on request."), S["body"]))
    doc.build(f)
    return buf.getvalue()


def cover_pdf(pack):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    S = _pdf_styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm,
                            title=f"{facts.CONTACT['name']} - Cover Letter", author=facts.CONTACT["name"])
    flow = []
    for text, kw in _cover_lines(pack):
        style = S["name"] if kw.get("size") == 14 else S["small"] if kw.get("size") == 9.5 else S["letter"]
        flow.append(Paragraph(f"<b>{_e(text)}</b>" if kw.get("bold") and style is S["letter"] else _e(text), style))
        if kw.get("after", 8) >= 12:
            flow.append(Spacer(1, 6))
    doc.build(flow)
    return buf.getvalue()


def file_stub(pack):
    import re
    comp = re.sub(r"[^A-Za-z0-9]+", "_", pack["job"].get("company") or "Company").strip("_")[:28] or "Company"
    return f"Satish_Gajjala_{comp}"


def render_all(pack):
    """{filename: bytes} for resume and cover letter in DOCX and PDF."""
    stub = file_stub(pack)
    return {
        f"{stub}_Resume.docx": resume_docx(pack),
        f"{stub}_Resume.pdf": resume_pdf(pack),
        f"{stub}_Cover_Letter.docx": cover_docx(pack),
        f"{stub}_Cover_Letter.pdf": cover_pdf(pack),
    }
