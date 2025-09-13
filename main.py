import csv
import os
import re
from shopify_client import ShopifyClient

def load_product_id_map(filepath="sheets/product_map/product_ids.csv"):
  id_map = {}
  with open(filepath, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
      sku = row.get("sku") or row.get("SKU")
      product_id = row.get("product_id")
      if sku and product_id:
        id_map[sku.strip()] = product_id.strip()
  return id_map

def make_title_from_url(url: str) -> str:
    basename = os.path.basename(url)            # "KS-Tech-UFS389006DA.pdf"
    filename, _ = os.path.splitext(basename)    # "KS-Tech-UFS389006DA"

    # Replace dashes/underscores with spaces
    words = re.split(r"[-_]+", filename)

    pretty_words = []
    for word in words:
        if word.isupper() or any(char.isdigit() for char in word):
            # Keep acronyms/codes unchanged
            pretty_words.append(word)
        else:
            # Capitalize like normal English
            pretty_words.append(word.capitalize())

    return " ".join(pretty_words)

shopify = ShopifyClient()

# ---------------- Example usage ----------------
if __name__ == "__main__":

  id_map = load_product_id_map("sheets/product_map/product_ids.csv")

  PRODUCT_DATA = {}

  with open("sheets/sku-url.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      sku = row["SKU"].strip()
      url = row["URL"].strip()

      product_id = id_map.get(sku)

      if not product_id:
        print(f"❌ No product ID found in map for SKU {sku}")
        continue

      if product_id not in PRODUCT_DATA:
        PRODUCT_DATA[product_id] = []

      entry = {
        "url": url,
        "title": make_title_from_url(url),
        "filename": os.path.basename(url)
      }

      if entry not in PRODUCT_DATA[product_id]:
        PRODUCT_DATA[product_id].append(entry)

  # print results
  for product_id, files in PRODUCT_DATA.items():
    print(f"Uploading files for product ID {product_id}:")

    uploaded_file_ids = []

    # 1. upload all PDFs
    for pdf in files:
      file_id = shopify.upload_pdf(pdf["url"], pdf["title"], pdf.get("filename", pdf["title"]))
      if file_id:
        uploaded_file_ids.append(file_id)

    print(uploaded_file_ids)

    # 2. attach all at once
    if uploaded_file_ids:
      shopify.add_files_to_product(product_id, uploaded_file_ids)
