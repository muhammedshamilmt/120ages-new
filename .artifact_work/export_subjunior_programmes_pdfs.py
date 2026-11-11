import os
from openpyxl import load_workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

INPUTS = [
    "/Users/apple/Downloads/Programmes_SUB-JUNIOR_ARTS_NON-STAGE_INDIVIDUAL_2026-09-27.xlsx",
    "/Users/apple/Downloads/Programmes_SUB-JUNIOR_ARTS_STAGE_INDIVIDUAL_2026-09-27.xlsx",
]
DISPLAY_TITLES = {
    "Programmes_SUB-JUNIOR_ARTS_NON-STAGE_INDIVIDUAL_2026-09-27.xlsx": "Arts-Non-stage-Sub-junior-Individual.pdf",
    "Programmes_SUB-JUNIOR_ARTS_STAGE_INDIVIDUAL_2026-09-27.xlsx": "Arts-Stage-Sub-junior-Individual.pdf",
}
OUTPUT_DIR = os.path.abspath("outputs/event_programmes/pdf_sheets")
EXCLUDED_HEADERS = {
    "Required / Team",
    "Max / Team",
    "1st Place Points",
    "2nd Place Points",
    "3rd Place Points",
    "Participation Points",
}
PAGE_WIDTH, _ = A4
LEFT = 50
TABLE_WIDTH = 495
COLUMN_WIDTHS = [42, 52, 137, 52, 66, 60, 58, 28]
TITLE_BAND_Y = 737
TITLE_BAND_HEIGHT = 46
HEADER_HEIGHT = 13
ROW_HEIGHT = 12.1
GRID = colors.HexColor("#D0D0D0")

def fitted_font(pdf, text, width, preferred=7.0, minimum=5.2):
    size = preferred
    while size > minimum and stringWidth(text, "Helvetica", size) > width - 6:
        size -= 0.2
    pdf.setFont("Helvetica", max(size, minimum))

def draw_cell(pdf, text, x, baseline, width, align="left", preferred=7.0):
    content = "" if text is None else str(text).strip()
    fitted_font(pdf, content, width, preferred)
    if align == "right":
        pdf.drawRightString(x + width - 3, baseline, content)
    elif align == "center":
        pdf.drawCentredString(x + width / 2, baseline, content)
    else:
        pdf.drawString(x + 3, baseline, content)

def extract_rows(path):
    workbook = load_workbook(path, data_only=True, read_only=True)
    worksheet = workbook.active
    source_rows = list(worksheet.iter_rows(values_only=True))
    headers = list(source_rows[0])
    keep = [i for i, header in enumerate(headers) if header not in EXCLUDED_HEADERS]
    retained_headers = [headers[i] for i in keep]
    retained_rows = [[row[i] if i < len(row) else None for i in keep] for row in source_rows[1:] if any(value is not None for value in row)]
    if len(retained_headers) != 8:
        raise ValueError(f"Expected 8 retained columns, found {len(retained_headers)}")
    return retained_headers, retained_rows

def draw_pdf(path):
    headers, rows = extract_rows(path)
    source_name = os.path.basename(path)
    title = DISPLAY_TITLES[source_name]
    output = os.path.join(OUTPUT_DIR, f"{source_name.rsplit('.', 1)[0]}.pdf")
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setTitle(title)
    pdf.setFillColor(colors.black)
    pdf.rect(LEFT, TITLE_BAND_Y, TABLE_WIDTH, TITLE_BAND_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    title_size = 14
    while title_size > 10 and stringWidth(title, "Helvetica", title_size) > TABLE_WIDTH - 20:
        title_size -= 0.5
    pdf.setFont("Helvetica", title_size)
    pdf.drawCentredString(PAGE_WIDTH / 2, TITLE_BAND_Y + 17, title)

    table_top = TITLE_BAND_Y
    table_bottom = table_top - HEADER_HEIGHT - len(rows) * ROW_HEIGHT
    if table_bottom < 56:
        raise ValueError(f"Data does not fit one page: {title}")
    pdf.setStrokeColor(GRID)
    pdf.setLineWidth(0.35)
    x = LEFT
    for width in COLUMN_WIDTHS:
        pdf.line(x, table_bottom, x, table_top)
        x += width
    pdf.line(LEFT + TABLE_WIDTH, table_bottom, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top - HEADER_HEIGHT, LEFT + TABLE_WIDTH, table_top - HEADER_HEIGHT)
    for row_number in range(len(rows) + 1):
        y = table_top - HEADER_HEIGHT - row_number * ROW_HEIGHT
        pdf.line(LEFT, y, LEFT + TABLE_WIDTH, y)

    pdf.setFillColor(colors.black)
    x = LEFT
    for i, header in enumerate(headers):
        draw_cell(pdf, header, x, table_top - 9.4, COLUMN_WIDTHS[i], "center" if i in (0, 7) else "left", 6.5)
        x += COLUMN_WIDTHS[i]
    for row_number, row in enumerate(rows):
        baseline = table_top - HEADER_HEIGHT - 8.5 - row_number * ROW_HEIGHT
        x = LEFT
        for i, value in enumerate(row):
            draw_cell(pdf, value, x, baseline, COLUMN_WIDTHS[i], "right" if i == 0 else "left")
            x += COLUMN_WIDTHS[i]
    pdf.showPage()
    pdf.save()
    return output

os.makedirs(OUTPUT_DIR, exist_ok=True)
for item in INPUTS:
    draw_pdf(item)
