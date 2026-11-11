import os
from openpyxl import load_workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

INPUTS = [
    ("ADL", "/Users/apple/Downloads/Candidates_ADL_2026-09-27.xlsx"),
    ("QIY", "/Users/apple/Downloads/Candidates_QIY_2026-09-27.xlsx"),
    ("SHJ", "/Users/apple/Downloads/Candidates_SHJ_2026-09-27.xlsx"),
]
OUTPUT_DIR = os.path.abspath("outputs/event_programmes/candidate_pdfs")
OUTPUT_NAME = "Candidates-ADL-QIY-SHJ.pdf"
PAGE_WIDTH, _ = A4
LEFT = 26
GRID_WIDTH = 176
GAP = 7
CHEST_WIDTH = 50
NAME_WIDTH = 126
TITLE_Y = 746
TITLE_HEIGHT = 40
TEAM_Y = 710
TEAM_HEIGHT = 18
HEADER_HEIGHT = 14
ROW_HEIGHT = 10.6
GRID = colors.HexColor("#D0D0D0")

def load_candidates(path):
    workbook = load_workbook(path, data_only=True, read_only=True)
    rows = list(workbook.active.iter_rows(values_only=True))
    headers = list(rows[0])
    chest_index = headers.index("Chest Number")
    candidate_index = headers.index("Candidate Name")
    return [(row[chest_index], row[candidate_index]) for row in rows[1:] if any(value is not None for value in row)]

def centered_text(pdf, value, x, baseline, width, preferred_size=7.5):
    text = "" if value is None else str(value).strip()
    size = preferred_size
    while size > 5.0 and stringWidth(text, "Helvetica", size) > width - 8:
        size -= 0.2
    pdf.setFont("Helvetica", size)
    pdf.drawCentredString(x + width / 2, baseline, text)

def draw_team_grid(pdf, team, candidates, x):
    table_top = TEAM_Y - TEAM_HEIGHT
    table_bottom = table_top - HEADER_HEIGHT - len(candidates) * ROW_HEIGHT
    if table_bottom < 48:
        raise ValueError(f"Team {team} will not fit on one page")
    pdf.setFillColor(colors.black)
    pdf.rect(x, TEAM_Y - TEAM_HEIGHT, GRID_WIDTH, TEAM_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(x + GRID_WIDTH / 2, TEAM_Y - 12, team)

    pdf.setStrokeColor(GRID)
    pdf.setLineWidth(0.35)
    for line_x in [x, x + CHEST_WIDTH, x + GRID_WIDTH]:
        pdf.line(line_x, table_bottom, line_x, table_top)
    pdf.line(x, table_top, x + GRID_WIDTH, table_top)
    pdf.line(x, table_top - HEADER_HEIGHT, x + GRID_WIDTH, table_top - HEADER_HEIGHT)
    for row_number in range(len(candidates) + 1):
        y = table_top - HEADER_HEIGHT - row_number * ROW_HEIGHT
        pdf.line(x, y, x + GRID_WIDTH, y)
    pdf.setFillColor(colors.black)
    centered_text(pdf, "Chest Number", x, table_top - 9.6, CHEST_WIDTH, 6.4)
    centered_text(pdf, "Candidate Name", x + CHEST_WIDTH, table_top - 9.6, NAME_WIDTH, 6.4)
    for row_number, (chest, name) in enumerate(candidates):
        baseline = table_top - HEADER_HEIGHT - 7.8 - row_number * ROW_HEIGHT
        centered_text(pdf, chest, x, baseline, CHEST_WIDTH)
        centered_text(pdf, name, x + CHEST_WIDTH, baseline, NAME_WIDTH)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    teams = [(team, load_candidates(path)) for team, path in INPUTS]
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    pdf = canvas.Canvas(output_path, pagesize=A4)
    pdf.setTitle(OUTPUT_NAME)
    pdf.setFillColor(colors.black)
    pdf.rect(LEFT, TITLE_Y, PAGE_WIDTH - 2 * LEFT, TITLE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(PAGE_WIDTH / 2, TITLE_Y + 14, OUTPUT_NAME)
    for index, (team, candidates) in enumerate(teams):
        draw_team_grid(pdf, team, candidates, LEFT + index * (GRID_WIDTH + GAP))
    pdf.showPage()
    pdf.save()
    return output_path

main()
