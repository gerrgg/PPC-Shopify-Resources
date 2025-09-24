from shopify_client import ShopifyClient
import csv

shopify = ShopifyClient()

if __name__ == "__main__":
    with open("sheets/product_map/product_ids.csv", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            product_id = row["product_id"]
            print(f"Processing product ID: {product_id}")
            shopify.delete_resources_metafield(product_id)
