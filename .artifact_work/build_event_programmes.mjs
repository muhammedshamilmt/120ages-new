import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputDir = "/Users/apple/Downloads";
const outputDir = path.resolve("outputs/event_programmes");
const files = [
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
];

const sheetNames = [
  "Arts NS Senior Ind",
  "Arts NS Subjun Ind",
  "Arts Stage Jr Group",
  "Arts Stage Sr Group",
  "Arts Stage Sr Ind",
  "Arts Stage Subjun Grp",
  "Arts Stage Subjun Ind",
  "Sports General Group",
  "Sports Junior Group",
  "Sports Senior Group",
  "Sports Senior Ind",
  "Sports Subjun Group",
  "Sports Subjun Ind",
];

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows.filter((values) => values.some((value) => value !== ""));
}

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function asTypedRow(row, header) {
  return row.map((value, index) => {
    if ((header[index] === "Sl. No." || header[index] === "Required Participants") && /^\d+$/.test(value.trim())) {
      return Number(value.trim());
    }
    return value.trim();
  });
}

await fs.mkdir(outputDir, { recursive: true });
const parsed = [];
for (const filename of files) {
  const raw = await fs.readFile(path.join(inputDir, filename), "utf8");
  const rows = parseCsv(raw.replace(/^\uFEFF/, ""));
  if (rows.length < 2 || rows[0].length !== 8) throw new Error(`Unexpected CSV layout: ${filename}`);
  parsed.push({ filename, title: filename.replace(/\.csv$/i, ""), header: rows[0], rows: rows.slice(1) });
}

const workbook = Workbook.create();
for (let index = 0; index < parsed.length; index += 1) {
  const source = parsed[index];
  const sheet = workbook.worksheets.add(sheetNames[index]);
  sheet.showGridLines = false;
  sheet.getRange("A1:H1").format = {
    fill: "#17365D",
    font: { name: "Arial", size: 14, bold: true, color: "#FFFFFF" },
    verticalAlignment: "center",
  };
  sheet.getRange("A1").values = [[source.title]];
  sheet.getRange("A1:H1").format.rowHeight = 26;
  sheet.getRange("A3:H3").values = [source.header];
  sheet.getRange("A3:H3").format = {
    fill: "#1F4E78",
    font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: "#D9E2F3" },
  };
  sheet.getRange("A3:H3").format.rowHeight = 32;
  const data = source.rows.map((row) => asTypedRow(row, source.header));
  sheet.getRangeByIndexes(3, 0, data.length, 8).values = data;
  const dataRange = sheet.getRangeByIndexes(3, 0, data.length, 8);
  dataRange.format = {
    font: { name: "Arial", size: 10, color: "#1F1F1F" },
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: "#D9E2F3" },
  };
  sheet.getRangeByIndexes(3, 0, data.length, 1).format.horizontalAlignment = "center";
  sheet.getRangeByIndexes(3, 6, data.length, 1).format.horizontalAlignment = "center";
  sheet.getRangeByIndexes(3, 7, data.length, 1).format.horizontalAlignment = "center";
  sheet.getRange(`A4:H${data.length + 3}`).format.autofitRows();
  const widths = [10, 14, 34, 13, 15, 16, 18, 12];
  widths.forEach((width, col) => { sheet.getRangeByIndexes(0, col, data.length + 3, 1).format.columnWidth = width; });
  sheet.freezePanes.freezeRows(3);
}

workbook.recalculate();
const exportFile = await SpreadsheetFile.exportXlsx(workbook);
await exportFile.save(path.join(outputDir, "Arts-and-Sports-Programmes.xlsx"));

const combinedHeader = ["Source File", ...parsed[0].header];
const combinedRows = parsed.flatMap((source) => source.rows.map((row) => [source.title, ...row.map((value) => value.trim())]));
const combinedCsv = [combinedHeader, ...combinedRows].map((row) => row.map(csvEscape).join(",")).join("\n") + "\n";
await fs.writeFile(path.join(outputDir, "Arts-and-Sports-Programmes-Combined.csv"), combinedCsv, "utf8");

const summary = {
  files: parsed.map((source) => ({ source: source.filename, records: source.rows.length })),
  totalRecords: combinedRows.length,
};
await fs.writeFile(path.join(outputDir, "summary.json"), JSON.stringify(summary, null, 2));

for (const sheetName of [sheetNames[0], sheetNames[4], sheetNames[12]]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1.5, format: "png" });
  await fs.writeFile(path.join(outputDir, `${sheetName.replace(/[^A-Za-z0-9]+/g, "-")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
