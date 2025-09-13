from shopify_client import ShopifyClient

# Example product + PDFs
PRODUCT_ID = "8024818090073"
FILES_TO_UPLOAD = [
  {
      "url": "https://kstrong.com/wp-content/uploads/KS-Tech-UFS389006DA.pdf",
      "title": "User Instruction Manual",
      "filename": "manual.pdf"
  },
  {
      "url": "https://kstrong.com/wp-content/uploads/KS-Tech-UFS389006DA.pdf",
      "title": "Tech Sheet",
      "filename": "tech-sheet.pdf"
  }
]

shopify = ShopifyClient()

uploaded_files = []
for f in FILES_TO_UPLOAD:
    file_id = shopify.upload_pdf(f["url"], f["title"], f["filename"])
    if file_id:
        uploaded_files.append(file_id)

if uploaded_files:
    shopify.add_files_to_product(PRODUCT_ID, uploaded_files)
