import csv
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

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
    "Sports-Junior-Individual.csv",
    "Arts-General-Group.csv",
    "Arts-Non-stage-Junior-Individual.csv",
    "Arts-Stage-Senior-Individual (1).csv",
    "Sports-Junior-Group (1).csv",
    "Arts-Stage-Junior-Individual.csv",
]

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 50
TABLE_WIDTH = 495
COLUMN_WIDTHS = [52, 55, 111, 52, 54, 55, 70, 46]
TITLE_BAND_Y = 737
TITLE_BAND_HEIGHT = 46
HEADER_HEIGHT = 13
ROW_HEIGHT = 12.1
GRID = colors.HexColor("#D0D0D0")

def set_fitted_font(pdf, text, available_width, preferred_size=7.1, minimum_size=5.4):
    size = preferred_size
    while size > minimum_size and stringWidth(text, "Helvetica", size) > available_width:
        size -= 0.2
    pdf.setFont("Helvetica", max(size, minimum_size))

def draw_text(pdf, text, x, y, width, align="left", preferred_size=7.1):
    content = str(text).strip()
    padding = 3
    set_fitted_font(pdf, content, width - 2 * padding, preferred_size)
    if align == "right":
        pdf.drawRightString(x + width - padding, y, content)
    elif align == "center":
        pdf.drawCentredString(x + width / 2, y, content)
    else:
        pdf.drawString(x + padding, y, content)

def draw_table(pdf, rows):
    table_top = TITLE_BAND_Y
    row_count = len(rows) - 1
    table_bottom = table_top - HEADER_HEIGHT - row_count * ROW_HEIGHT
    if table_bottom < 56:
        raise ValueError(f"Data does not fit a single page: {row_count} rows")

    pdf.setStrokeColor(GRID)
    pdf.setLineWidth(0.35)
    x = LEFT
    for width in COLUMN_WIDTHS:
        pdf.line(x, table_bottom, x, table_top)
        x += width
    pdf.line(LEFT + TABLE_WIDTH, table_bottom, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top, LEFT + TABLE_WIDTH, table_top)
    pdf.line(LEFT, table_top - HEADER_HEIGHT, LEFT + TABLE_WIDTH, table_top - HEADER_HEIGHT)
    for number in range(row_count + 1):
        y = table_top - HEADER_HEIGHT - number * ROW_HEIGHT
        pdf.line(LEFT, y, LEFT + TABLE_WIDTH, y)

    baseline = table_top - 9.4
    x = LEFT
    for index, value in enumerate(rows[0]):
        alignment = "center" if index in (0, 6, 7) else "left"
        draw_text(pdf, value, x, baseline, COLUMN_WIDTHS[index], alignment, 6.8)
        x += COLUMN_WIDTHS[index]

    for row_number, row in enumerate(rows[1:]):
        baseline = table_top - HEADER_HEIGHT - 8.5 - row_number * ROW_HEIGHT
        x = LEFT
        for index, value in enumerate(row):
            alignment = "right" if index in (0, 6) else "left"
            draw_text(pdf, value, x, baseline, COLUMN_WIDTHS[index], alignment)
            x += COLUMN_WIDTHS[index]

def create_pdf(filename):
    title = filename[:-4]
    output_path = os.path.join(OUTPUT_DIR, f"{title}.pdf")
    with open(os.path.join(INPUT_DIR, filename), newline="", encoding="utf-8-sig") as source:
        rows = list(csv.reader(source))
    pdf = canvas.Canvas(output_path, pagesize=A4)
    pdf.setTitle(title)
    pdf.setFillColor(colors.black)
    pdf.rect(LEFT, TITLE_BAND_Y, TABLE_WIDTH, TITLE_BAND_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(PAGE_WIDTH / 2, TITLE_BAND_Y + 17, title)
    pdf.setFillColor(colors.black)
    draw_table(pdf, rows)
    pdf.showPage()
    pdf.save()

os.makedirs(OUTPUT_DIR, exist_ok=True)
for item in FILES:
    if os.path.exists(os.path.join(INPUT_DIR, item)):
        create_pdf(item)
    elif not os.path.exists(os.path.join(OUTPUT_DIR, f"{item[:-4]}.pdf")):
        raise FileNotFoundError(f"Missing source CSV and existing PDF: {item}")
