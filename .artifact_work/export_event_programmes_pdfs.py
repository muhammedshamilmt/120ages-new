import csv
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

INPUT_DIR = "/Users/apple/Downloads"
OUTPUT_DIR = os.path.abspath("outputs/event_programmes/pdf_sheets")
FILES = [
    "Arts-Non-stage-Senior-Individual.csv",
    "Arts-Non-stage-Sub-junior-Individual.csv",
    "Arts-Stage-Junior-Group.csv",
    "Arts-Stage-Senior-Group.csv",
    "Arts-Stage-Senior-Individual.csv",
    "Arts-Stage-Sub-junior-Group.csv",
    "Arts-Stage-Sub-junior-Individual.csv",
    "Sports-General-Group.csv",
    "Sports-Junior-Group.csv",
    "Sports-Senior-Group.csv",
    "Sports-Senior-Individual.csv",
    "Sports-Sub-junior-Group.csv",
    "Sports-Sub-junior-Individual.csv",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "SheetTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15,
    leading=18, textColor=colors.HexColor("#17365D"), spaceAfter=8,
)
body_style = ParagraphStyle("Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5, leading=9)
head_style = ParagraphStyle("Header", parent=body_style, fontName="Helvetica-Bold", textColor=colors.white, alignment=1)
widths = [14*mm, 18*mm, 61*mm, 22*mm, 25*mm, 25*mm, 29*mm, 18*mm]

for filename in FILES:
    title = filename[:-4]
    with open(os.path.join(INPUT_DIR, filename), newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    table_data = [[Paragraph(cell, head_style) for cell in rows[0]]]
    for row in rows[1:]:
        table_data.append([Paragraph(cell.strip(), body_style) for cell in row])
    document = SimpleDocTemplate(
        os.path.join(OUTPUT_DIR, f"{title}.pdf"), pagesize=landscape(A4),
        leftMargin=10*mm, rightMargin=10*mm, topMargin=22*mm, bottomMargin=14*mm,
        title=title,
    )
    table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (6, 1), (7, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2F3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    def add_page_header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 15)
        canvas.setFillColor(colors.HexColor("#17365D"))
        canvas.drawString(document.leftMargin, landscape(A4)[1] - 12*mm, title)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawRightString(landscape(A4)[0] - document.rightMargin, 7*mm, f"Page {doc.page}")
        canvas.restoreState()
    document.build([table], onFirstPage=add_page_header_footer, onLaterPages=add_page_header_footer)
