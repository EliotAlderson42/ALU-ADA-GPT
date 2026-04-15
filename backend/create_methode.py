"""
Generation d'un memoire technique PDF modulable (chapitres, sous-chapitres, tableaux)
via ReportLab.
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _to_str(value) -> str:
    if value is None:
        return ""
    return str(value)


def create_memoire_payload(body: dict) -> dict:
    """Normalise le payload recu du frontend."""
    payload = body if isinstance(body, dict) else {}
    return {
        "title": _to_str(payload.get("title")) or "MEMOIRE TECHNIQUE",
        "group_label": _to_str(payload.get("group_label")),
        "project_title": _to_str(payload.get("project_title")),
        "intro": _to_str(payload.get("intro")),
        "chapters": payload.get("chapters") if isinstance(payload.get("chapters"), list) else [],
    }


def fill_memoire_docx(payload: dict) -> None:
    """
    Conserve le nom historique de fonction pour compatibilite,
    mais genere un PDF ReportLab : backend/output/memoire_technique.pdf
    """
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "memoire_technique.pdf")

    # Couleurs proches du PDF exemple (sobre, bleu fonce + gris)
    blue_dark = colors.HexColor("#0F2F56")
    blue_mid = colors.HexColor("#1F4E79")
    gray_border = colors.HexColor("#C9D1DB")
    gray_text = colors.HexColor("#2F3C4A")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "MemoTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=blue_dark,
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "MemoSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=blue_mid,
        spaceAfter=4,
    )
    chapter_style = ParagraphStyle(
        "MemoChapter",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=blue_dark,
        spaceBefore=10,
        spaceAfter=6,
    )
    section_style = ParagraphStyle(
        "MemoSection",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14,
        textColor=blue_mid,
        spaceBefore=6,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "MemoBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=gray_text,
        spaceAfter=3,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=1.6 * cm,
        bottomMargin=1.4 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
    )
    flow = []

    flow.append(Paragraph(_to_str(payload.get("title")) or "MEMOIRE TECHNIQUE", title_style))
    group_label = _to_str(payload.get("group_label"))
    project_title = _to_str(payload.get("project_title"))
    intro = _to_str(payload.get("intro"))
    if group_label:
        flow.append(Paragraph(group_label, subtitle_style))
    if project_title:
        flow.append(Paragraph(project_title, subtitle_style))
    if intro:
        for line in intro.splitlines():
            if line.strip():
                flow.append(Paragraph(line.strip(), body_style))
    flow.append(Spacer(1, 0.25 * cm))

    for chapter in payload.get("chapters", []):
        if not isinstance(chapter, dict) or not chapter.get("enabled", True):
            continue
        chapter_title = _to_str(chapter.get("title")) or "Chapitre"
        flow.append(Paragraph(chapter_title, chapter_style))

        chapter_intro = _to_str(chapter.get("intro"))
        if chapter_intro:
            for line in chapter_intro.splitlines():
                if line.strip():
                    flow.append(Paragraph(line.strip(), body_style))

        sections = chapter.get("sections")
        if not isinstance(sections, list):
            continue
        for section in sections:
            if not isinstance(section, dict) or not section.get("enabled", True):
                continue
            section_title = _to_str(section.get("title")) or "Sous-chapitre"
            flow.append(Paragraph(section_title, section_style))

            content = _to_str(section.get("content"))
            if content:
                for line in content.splitlines():
                    if line.strip():
                        flow.append(Paragraph(line.strip(), body_style))

            table = section.get("table")
            if not isinstance(table, dict) or not table.get("enabled", False):
                continue
            columns = table.get("columns") if isinstance(table.get("columns"), list) else []
            rows = table.get("rows") if isinstance(table.get("rows"), list) else []
            if not columns:
                continue

            table_title = _to_str(table.get("title"))
            if table_title:
                flow.append(Paragraph(table_title, subtitle_style))

            table_data = [[_to_str(c) for c in columns]]
            for row in rows:
                if isinstance(row, list):
                    table_data.append([_to_str(row[i]) if i < len(row) else "" for i in range(len(columns))])

            col_width = (doc.width / max(1, len(columns)))
            t = Table(table_data, colWidths=[col_width] * len(columns), repeatRows=1)
            t.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("TEXTCOLOR", (0, 1), (-1, -1), gray_text),
                        ("BACKGROUND", (0, 0), (-1, 0), blue_mid),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F9FC")),
                        ("GRID", (0, 0), (-1, -1), 0.5, gray_border),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            flow.append(t)
            flow.append(Spacer(1, 0.2 * cm))

    doc.build(flow)
