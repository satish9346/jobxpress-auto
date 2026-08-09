"""
Turns plain-text resume / cover letter into clean, ATS-friendly PDFs.
Kept deliberately simple: standard fonts, clear headings, no graphics —
exactly what applicant-tracking systems parse best.
"""
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import HexColor

def _styles():
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=9.5, leading=13, alignment=TA_LEFT)
    name = ParagraphStyle("name", parent=body, fontName="Helvetica-Bold",
                          fontSize=16, leading=19, spaceAfter=2)
    head = ParagraphStyle("head", parent=body, fontName="Helvetica-Bold",
                          fontSize=10.5, leading=14, textColor=HexColor("#1F4FE0"),
                          spaceBefore=8, spaceAfter=3)
    return body, name, head

def _esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _looks_heading(line):
    s = line.strip()
    if not s or len(s) > 40:
        return False
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)

def text_to_pdf(text, title="document"):
    """Generic plain-text -> PDF. ALL-CAPS short lines become blue headings."""
    body, name, head = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=16*mm, rightMargin=16*mm,
                            topMargin=14*mm, bottomMargin=14*mm, title=title)
    flow, first = [], True
    for raw in (text or "").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flow.append(Spacer(1, 4))
            continue
        if first:
            flow.append(Paragraph(_esc(line), name)); first = False; continue
        if _looks_heading(line):
            flow.append(Paragraph(_esc(line), head))
        else:
            bullet = line.lstrip().startswith(("-", "•", "*"))
            txt = _esc(line.lstrip("-•* ").rstrip())
            if bullet:
                txt = "•&nbsp;&nbsp;" + txt
            flow.append(Paragraph(txt, body))
    doc.build(flow)
    return buf.getvalue()

def resume_pdf(text):
    return text_to_pdf(text, "Resume")

def cover_pdf(text):
    return text_to_pdf(text, "Cover Letter")
