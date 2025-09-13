import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # load env vars from .env


class ShopifyClient:
    def __init__(self):
        self.store = os.getenv("SHOPIFY_STORE")
        self.token = os.getenv("ACCESS_TOKEN")
        if not self.store or not self.token:
            raise ValueError("Missing SHOPIFY_STORE or ACCESS_TOKEN in .env")

        self.url = f"https://{self.store}/admin/api/2025-07/graphql.json"
        self.headers = {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        }

    def make_request(self, query, variables=None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(self.url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"GraphQL request failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

    def _normalize_product_gid(self, product_id: str) -> str:
      # Accept both numeric IDs and full GIDs
      return product_id if product_id.startswith("gid://") else f"gid://shopify/Product/{product_id}"

    # ----------------- Variant helpers -----------------
    def get_parent_id_from_sku(self, sku):
        query = """
        query getProductBySku($sku: String!) {
          productVariants(first: 1, query: $sku) {
            edges {
              node {
                id
                sku
                product {
                  id
                  title
                }
              }
            }
          }
        }
        """
        variables = {"sku": f"sku:{sku}"}
        response = self.make_request(query, variables)

        variant_edges = (
            response.get("data", {}).get("productVariants", {}).get("edges", [])
        )
        if not variant_edges:
            raise Exception(f"No product found with SKU: {sku}")

        return variant_edges[0]["node"]["product"]["id"]

    # ----------------- File helpers -----------------
    def upload_pdf(self, pdf_url, title, filename):
        query = """
        mutation fileCreate($files: [FileCreateInput!]!) {
          fileCreate(files: $files) {
            files {
              ... on GenericFile {
                id
                url
                alt
                fileStatus
                createdAt
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {
            "files": [
                {
                    "alt": title,
                    "filename": filename,
                    "contentType": "FILE",
                    "originalSource": pdf_url,
                }
            ]
        }
        data = self.make_request(query, variables)
        errors = data.get("data", {}).get("fileCreate", {}).get("userErrors", [])
        if errors:
            print(f"❌ Errors uploading {filename}:", errors)
            return None
        file_id = data["data"]["fileCreate"]["files"][0]["id"]
        print(f"✅ Uploaded {filename}: {file_id}")

        return file_id

    def add_files_to_product(self, product_id, file_entries):
        """
        Stores multiple files in a product metafield (list.file_reference)
        """
        metafield_value = json.dumps(file_entries)

        query = """
          mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
            metafieldsSet(metafields: $metafields) {
              metafields { id namespace key value type ownerType }
              userErrors { field message }
            }
          }
        """
        variables = {
            "metafields": [
                {
                    "ownerId": self._normalize_product_gid(product_id),
                    "namespace": "fpusa",
                    "key": "resources",
                    "type": "list.file_reference",
                    "value": metafield_value,
                }
            ]
        }

        data = self.make_request(query, variables)
        errors = data.get("data", {}).get("metafieldsSet", {}).get("userErrors", [])
        if errors:
            print("❌ Errors adding metafield:", errors)
        else:
            print("✅ All files added to product successfully!")
