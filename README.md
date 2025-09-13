# Shopify Product Resource Uploader

This project automates attaching resource files (like PDFs) to Shopify products via the **Shopify GraphQL Admin API**.  
It is designed to migrate and manage product resources from an external source (e.g., an old site) into Shopify product metafields.

---

## ✨ Features

- Query Shopify for product IDs from SKUs.
- Build a reusable SKU → Product ID mapping (`product_ids.csv`).
- Upload PDFs to Shopify’s file storage.
- Attach uploaded files to products in a metafield (`list.file_reference`).
- Generate human-friendly titles from file names for display in Shopify.
- Batch process many SKUs and files safely (with rate-limit handling).

---

## 📂 File Overview

- **`shopify_client.py`** → Core class for handling Shopify GraphQL requests, uploading files, and updating metafields.
- **`build_product_map.py`** → Standalone script that builds a `product_ids.csv` file from SKUs in your source CSV. Run this once to avoid querying Shopify repeatedly.
- **Main importer script** → Reads `sku-url.csv`, groups files by product, uploads them to Shopify, and attaches them to the correct product metafields.

---

## ⚙️ Setup

1. **Clone / Copy project** into your working directory.

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   (Your `requirements.txt` should include at least: `requests`, `python-dotenv`.)

4. **Set environment variables** in a `.env` file:
   ```env
   SHOPIFY_STORE=your-shop.myshopify.com
   ACCESS_TOKEN=shpat_xxxxxxxxxxxxx
   ```

---

## 📑 Workflow

### 1. Prepare input data

Your input CSV (`sheets/sku-url.csv`) should look like:

```csv
SKU,URL
12345-s,https://example.com/manual-s.pdf
12345-s,https://example.com/specs-s.pdf
12345-m,https://example.com/manual-m.pdf
```

### 2. Build product ID map

Run once to resolve all SKUs to Shopify product IDs:

```bash
python build_product_map.py
```

This generates:

- ✅ `sheets/product_ids.csv` → successful SKU → Product ID map
- ❌ `sheets/product_ids_fail.csv` → SKUs that couldn’t be resolved

### 3. Upload & attach files

Run the importer script. It will:

- Read `sku-url.csv`
- Match SKUs to product IDs from `product_ids.csv`
- Upload files to Shopify
- Attach them to the correct product under the metafield `fpusa.resources`

---

## 🚦 Rate Limits

Shopify’s GraphQL API uses a **cost-based throttle** (1,000 points available, refilling at ~50/sec).  
This project includes basic throttle handling, automatically pausing when usage is high.

---

## ✅ Example Output

```
✅ Found product ID gid://shopify/Product/987654321 for SKU 12345-s
✅ Uploading files for product ID gid://shopify/Product/987654321:
   ✅ Uploaded Manual S → gid://shopify/GenericFile/111
   ✅ Uploaded Specs S → gid://shopify/GenericFile/112
✅ All files added to product successfully!
```

---

## 🔮 Future Enhancements

- Resume support (skip already uploaded files).
- Merge new files into existing metafields instead of overwriting.
- More flexible title generation (keep acronyms, product codes).
