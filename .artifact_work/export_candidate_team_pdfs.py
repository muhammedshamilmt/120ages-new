import os
from openpyxl import load_workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

INPUTS = [
    ("/Users/apple/Downloads/Candidates_ADL_2026-09-27.xlsx", "Candidates-ADL.pdf"),
    ("/Users/apple/Downloads/Candidates_QIY_2026-09-27.xlsx", "Candidates-QIY.pdf"),
    ("/Users/apple/Downloads/Candidates_SHJ_2026-09-27.xlsx", "Candidates-SHJ.pdf"),
]
OUTPUT_DIR = os.path.abspath("outputs/event_programmes/candidate_pdfs")
PAGE_WIDTH, _ = A4
LEFT = 95
TABLE_WIDTH = 405
COLUMN_WIDTHS = [58, 92, 255]
TITLE_BAND_Y = 737
TITLE_BAND_HEIGHT = 46
HEADER_HEIGHT = 14
ROW_HEIGHT = 10.5
GRID = colors.HexColor("#D0D0D0")

def draw_text(pdf, value, x, baseline, width, alignment="left", preferred_size=7.8):
    text = "" if value is None else str(value).strip()
    size = preferred_size
    while size > 5.4 and stringWidth(text, "Helvetica", size) > width - 8:
        size -= 0.2
    pdf.setFont("Helvetica", size)
    if alignment == "right":
        pdf.drawRightString(x + width - 4, baseline, text)
    elif alignment == "center":
        pdf.drawCentredString(x + width / 2, baseline, text)
    else:
        pdf.drawString(x + 4, baseline, text)

def load_rows(path):
    workbook = load_workbook(path, data_only=True, read_only=True)
    worksheet = workbook.active
    rows = [list(row) for row in worksheet.iter_rows(values_only=True)]
    if not rows or len(rows[0]) != 3:
        raise ValueError(f"Expected a three-column candidate list: {path}")
    return rows[0], [row for row in rows[1:] if any(value is not None for value in row)]

def create_pdf(source_path, output_name):
    headers, rows = load_rows(source_path)
    output_path = os.path.join(OUTPUT_DIR, output_name)
    table_top = TITLE_BAND_Y
    table_bottom = table_top - HEADER_HEIGHT - len(rows) * ROW_HEIGHT
    if table_bottom < 56:
        raise ValueError(f"Candidate list will not fit on one page: {output_name}")
    pdf = canvas.Canvas(output_path, pagesize=A4)
    pdf.setTitle(output_name)
    pdf.setFillColor(colors.black)
    pdf.rect(LEFT, TITLE_BAND_Y, TABLE_WIDTH, TITLE_BAND_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(PAGE_WIDTH / 2, TITLE_BAND_Y + 17, output_name)
    pdf.setStrokeColor(GRID)
    pdf.setLineWidth(0.35)
    x = LEFT
    for width in COLUMN_WIDTHS:
        pdf.line(x, table_bottom, x, table_top)
        x += width
    pdf.line(LEFT + TABLE_WIDTH, table_bottom, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top - HEADER_HEIGHT, LEFT + TABLE_WIDTH, table_top - HEADER_HEIGHT)
    for index in range(len(rows) + 1):
        y = table_top - HEADER_HEIGHT - index * ROW_HEIGHT
        pdf.line(LEFT, y, LEFT + TABLE_WIDTH, y)
    pdf.setFillColor(colors.black)
    x = LEFT
    for index, header in enumerate(headers):
        draw_text(pdf, header, x, table_top - 9.8, COLUMN_WIDTHS[index], "center", 7.2)
        x += COLUMN_WIDTHS[index]
    for number, row in enumerate(rows):
        baseline = table_top - HEADER_HEIGHT - 7.7 - number * ROW_HEIGHT
        x = LEFT
        for index, value in enumerate(row):
            draw_text(pdf, value, x, baseline, COLUMN_WIDTHS[index], "center")
            x += COLUMN_WIDTHS[index]
    pdf.showPage()
    pdf.save()
    return output_path

os.makedirs(OUTPUT_DIR, exist_ok=True)
for source, output in INPUTS:
    create_pdf(source, output)
