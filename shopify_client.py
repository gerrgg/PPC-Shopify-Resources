import requests
import json
import os
from dotenv import load_dotenv

load_dotenv() 

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
      # First, try finding by variant SKU
      query_variant = """
      query getVariantBySku($sku: String!) {
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
      response = self.make_request(query_variant, variables)

      variant_edges = (
        response.get("data", {})
        .get("productVariants", {})
        .get("edges", [])
      )

      if variant_edges:
        return variant_edges[0]["node"]["product"]["id"]

      # If not found as a variant, try finding directly as a product
      query_product = """
      query getProductBySku($sku: String!) {
        products(first: 1, query: $sku) {
          edges {
            node {
              id
              title
            }
          }
        }
      }
      """
      response = self.make_request(query_product, variables)

      product_edges = (
        response.get("data", {})
        .get("products", {})
        .get("edges", [])
      )

      if product_edges:
        return product_edges[0]["node"]["id"]

      raise Exception(f"No product or variant found with SKU: {sku}")


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
      product_gid = self._normalize_product_gid(product_id)

      # Step 1: Fetch existing metafield
      query_fetch = """
        query getMetafield($id: ID!) {
          product(id: $id) {
            metafield(namespace: "fpusa", key: "resources") {
              value
              type
            }
          }
        }
      """
      existing_data = self.make_request(query_fetch, {"id": product_gid})
      
      existing_metafield = (
          existing_data.get("data", {})
          .get("product", {})
          .get("metafield", {})
      )

      existing_ids = []
      
      if existing_metafield and existing_metafield.get("value"):
          try:
              existing_ids = json.loads(existing_metafield["value"])
          except Exception:
              existing_ids = []

      # Step 2: Merge new file entries
      all_ids = list(set(existing_ids + file_entries))

      metafield_value = json.dumps(all_ids)

      # Step 3: Save back to product
      query_update = """
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
                  "ownerId": product_gid,
                  "namespace": "fpusa",
                  "key": "resources",
                  "type": "list.file_reference",
                  "value": metafield_value,
              }
          ]
      }

      data = self.make_request(query_update, variables)
      errors = data.get("data", {}).get("metafieldsSet", {}).get("userErrors", [])
      if errors:
          print("❌ Errors adding metafield:", errors)
      else:
          print(f"✅ Files merged and saved to product {product_gid} successfully!")
    
    def delete_resources_metafield(self, product_id):
      product_gid = self._normalize_product_gid(product_id)

      query = """
      mutation MetafieldsDelete($metafields: [MetafieldIdentifierInput!]!) {
        metafieldsDelete(metafields: $metafields) {
          deletedMetafields {
            key
            namespace
            ownerId
          }
          userErrors {
            field
            message
          }
        }
      }
      """

      variables = {
          "metafields": [
              {
                  "ownerId": product_gid,
                  "namespace": "fpusa",
                  "key": "resources"
              }
          ]
      }

      result = self.make_request(query, variables)
      errors = result.get("data", {}).get("metafieldsDelete", {}).get("userErrors", [])
      if errors:
          print(f"❌ Errors deleting metafield for {product_id}: {errors}")
      else:
          deleted = result.get("data", {}).get("metafieldsDelete", {}).get("deletedMetafields", [])
          print(f"✅ Deleted metafields {deleted} for product {product_id}")


    def getMetafield(self, product_id):
      query = """
      query getResourceMetafield($id: ID!) {
        product(id: $id) {
          id
          title
          metafield(namespace: "fpusa", key: "resources") {
            id
            namespace
            key
            type
            value
          }
        }
      }
      """
      product_gid = self._normalize_product_gid(product_id)
      response = self.make_request(query, {"id": product_gid})

      print(response)

      metafield = (
          response.get("data", {})
          .get("product", {})
          .get("metafield", {})
      )
      return metafield if metafield else None
