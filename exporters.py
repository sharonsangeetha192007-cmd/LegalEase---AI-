from io import BytesIO
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from fpdf import FPDF

from legal_ease.sanitization import sanitize_text


def _lines(text: str):
    return sanitize_text(text).splitlines()


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return (
        stripped.startswith("# ")
        or stripped.startswith("## ")
        or bool(re.match(r"^\d+(\.\d+)*[.)]\s+\S+", stripped))
        or stripped.isupper()
    )


def format_txt(text: str) -> bytes:
    return sanitize_text(text).encode("utf-8")


def format_docx(text: str, doc_type: str, logo_bytes: bytes | None = None) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    if logo_bytes:
        try:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(BytesIO(logo_bytes), width=Inches(1.2))
        except Exception:
            pass

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(doc_type.upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    for line in _lines(text):
        if not line.strip():
            doc.add_paragraph()
            continue

        stripped = line.strip()
        if stripped.startswith("# "):
            p = doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("## "):
            p = doc.add_heading(stripped[3:], level=2)
        elif _is_heading(stripped):
            p = doc.add_paragraph()
            r = p.add_run(stripped)
            r.bold = True
        elif re.match(r"^[-*]\s+", stripped):
            p = doc.add_paragraph(
                re.sub(r"^[-*]\s+", "", stripped), style="List Bullet"
            )
        else:
            p = doc.add_paragraph(stripped)

        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run(
        "LegalEase — Drafting assistance only. Review with a qualified legal professional."
    ).font.size = Pt(8)

    output = BytesIO()
    doc.save(output)
    return output.getvalue()


class _LegalEasePDF(FPDF):
    def __init__(self, doc_type: str, logo_path: str | None = None):
        super().__init__()
        self.doc_type = doc_type
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        if self.logo_path:
            try:
                self.image(self.logo_path, x=92, y=8, w=26)
                self.ln(17)
            except Exception:
                pass
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.doc_type.upper(), align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", size=7)
        self.cell(
            0,
            8,
            "LegalEase — Drafting assistance only; obtain professional legal review.",
            align="C",
        )


def format_pdf(text: str, doc_type: str, logo_path: str | None = None) -> bytes:
    pdf = _LegalEasePDF(doc_type, logo_path)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    for line in _lines(text):
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue

        if stripped.startswith("# "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(0, 8, stripped[2:])
            pdf.set_font("Helvetica", size=10)
        elif stripped.startswith("## ") or _is_heading(stripped):
            pdf.set_font("Helvetica", "B", 11)
            value = stripped.lstrip("#").strip()
            pdf.multi_cell(0, 7, value, wrapmode="CHAR")
            pdf.set_font("Helvetica", size=10)
        elif re.match(r"^[-*]\s+", stripped):
            pdf.multi_cell(0, 6, "- " + re.sub(r"^[-*]\s+", "", stripped))
        else:
            pdf.multi_cell(0, 6, stripped)

    return bytes(pdf.output(dest="S"))
