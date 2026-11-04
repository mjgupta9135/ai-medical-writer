from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _set_cell_shading(cell, fill="D9EAF7"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def build_docx(study_id: str, sections: list[dict], validation: dict, output_path: str) -> str:
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(0.75)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(11)
    styles["Normal"].paragraph_format.space_after = Pt(6)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("CLINICAL STUDY REPORT")
    run.bold = True
    run.font.size = Pt(20)
    title2 = doc.add_paragraph()
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title2.add_run(f"Study {study_id}").bold = True
    doc.add_paragraph("DRAFT — SYNTHETIC PROOF-OF-CONCEPT MATERIAL")
    doc.add_paragraph("NOT FOR CLINICAL OR REGULATORY USE")
    doc.add_page_break()

    doc.add_heading("Document status and review notice", level=1)
    doc.add_paragraph(
        "This document was generated automatically from supplied synthetic POC JSON inputs. "
        "It requires qualified medical writer, statistician, and sponsor review. It is not approved."
    )
    doc.add_paragraph(f"Validation status: {validation.get('validation_status', 'NOT_RUN')}")
    issues = validation.get("issues", [])
    if issues:
        doc.add_heading("Open validation findings", level=2)
        for issue in issues:
            doc.add_paragraph(str(issue), style="List Bullet")

    doc.add_page_break()
    doc.add_heading("Table of Contents", level=1)
    for item in sections:
        doc.add_paragraph(f"{item.get('number', '')} {item.get('title', '')}")
    doc.add_page_break()

    for item in sections:
        number = str(item.get("number", "")).strip()
        heading = f"{number} {item.get('title', 'Untitled section')}".strip()
        doc.add_heading(heading, level=1)
        content = item.get("content", "").strip()
        if not content:
            content = "[SOURCE INFORMATION NOT AVAILABLE — HUMAN REVIEW REQUIRED]"
        for paragraph in content.split("\n\n"):
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())
        refs = item.get("source_references", [])
        if refs:
            p = doc.add_paragraph()
            r = p.add_run("Sources: " + "; ".join(refs))
            r.italic = True
            r.font.size = Pt(9)
        notes = item.get("review_notes", [])
        if notes:
            doc.add_heading("Review notes", level=2)
            for note in notes:
                doc.add_paragraph(str(note), style="List Bullet")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return str(output)
