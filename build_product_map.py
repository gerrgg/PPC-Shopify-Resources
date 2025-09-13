import csv
from shopify_client import ShopifyClient

INPUT_CSV = "sheets/sku-url.csv"
OUTPUT_CSV = "sheets/product_map/product_ids.csv"
OUTPUT_FAIL_CSV = "sheets/product_map/product_ids_fail.csv"

def build_product_map():
  shopify = ShopifyClient()
  id_map = {}
  fail_map = []

  with open(INPUT_CSV, newline="") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
      sku = row.get("SKU") or row.get("sku")
      if not sku:
        continue
      sku = sku.strip()

      if sku in id_map or sku in fail_map:
        continue

      try:
        product_id = shopify.get_parent_id_from_sku(sku)
        print(f"✅ Found {sku} → {product_id}")
        id_map[sku] = product_id
      except Exception as e:
        fail_map.append(sku)
        print(f"❌ Could not fetch product ID for SKU {sku}: {e}")

  # Save successful lookups
  with open(OUTPUT_CSV, "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["sku", "product_id"])
    for sku, product_id in id_map.items():
      writer.writerow([sku, product_id])

  print(f"\n📄 Product ID map saved to {OUTPUT_CSV}")

  # Save failed lookups
  with open(OUTPUT_FAIL_CSV, "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["sku"])
    for sku in fail_map:
      writer.writerow([sku])

  print(f"\n📄 Fail map saved to {OUTPUT_FAIL_CSV}")

if __name__ == "__main__":
  build_product_map()
