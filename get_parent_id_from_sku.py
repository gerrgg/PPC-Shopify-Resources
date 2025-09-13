from shopify_client import ShopifyClient

# ---------------- Example usage ----------------
if __name__ == "__main__":
    PRODUCT_SKUS = ["12345-s", "12345-m", "12345-l"]

    shopify = ShopifyClient()

    for sku in PRODUCT_SKUS:
        try:
            parent_id = shopify.get_parent_id_from_sku(sku)
            print(f"SKU: {sku} -> Parent Product ID: {parent_id}")
        except Exception as e:
            print(f"Error fetching parent ID for SKU {sku}: {e}")
