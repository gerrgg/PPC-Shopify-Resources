import csv
import os
import glob
import re

def generate_title_from_filename(filename):
  name = os.path.splitext(filename)[0]
  name = re.sub(r'^\d+[_-]?', '', name)
  name = name.replace("_", " ").replace("-", " ")
  return name.title().strip()

def is_real_pdf(filepath):
  try:
    with open(filepath, "rb") as f:
      header = f.read(5)
      if not header.startswith(b"%PDF"):
        return False
      f.seek(-20, os.SEEK_END)
      trailer = f.read().strip()
      if b"%%EOF" not in trailer:
        return False
    return True
  except Exception:
    return False

# Paths
input_file = "input.csv"
output_file = "output.csv"
pdf_folder = "pdfs"

# Build PDF index by SKU
pdf_index = {}
skipped_pdfs = 0

for pdf in glob.glob(os.path.join(pdf_folder, "*.pdf")):
  if not is_real_pdf(pdf):
    print(f"⚠️ Skipping invalid/corrupt file: {pdf}")
    skipped_pdfs += 1
    continue

  filename = os.path.basename(pdf)
  sku = filename.split("_")[0].split(".")[0]
  pdf_index.setdefault(sku, []).append((pdf, generate_title_from_filename(filename)))

# Read input CSV
with open(input_file, newline="", encoding="utf-8") as f:
  reader = csv.DictReader(f)
  rows = list(reader)

# Write output CSV (only when PDFs exist)
fieldnames = ["ID", "SKU", "Generated_Title", "PDF_Path"]
seen = set()
skus_dropped = 0
written_rows = 0

with open(output_file, "w", newline="", encoding="utf-8") as f:
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()

  for row in rows:
    sku = row["SKU"]
    pdfs = pdf_index.get(sku, [])
    if not pdfs:
      skus_dropped += 1
      continue  # skip SKUs with no valid PDFs

    for pdf, title in pdfs:
      key = (sku, pdf)
      if key not in seen:
        seen.add(key)
        writer.writerow({
          "ID": row["ID"],
          "SKU": sku,
          "Generated_Title": title,
          "PDF_Path": pdf
        })
        written_rows += 1

print(f"✅ Done! Created {output_file}")
print(f"ℹ️ Skipped {skipped_pdfs} invalid/corrupt PDFs")
print(f"ℹ️ Dropped {skus_dropped} SKUs with no valid PDFs")
print(f"ℹ️ Wrote {written_rows} rows to output")
