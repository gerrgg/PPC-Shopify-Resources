# Plan

Goal: Import product resources from old site to new site

Basic Steps

- Get CSV File with SKU, Button Link, URL
- Loop CSV programically
  - Group up data by sku
  - Loop Data
    - Make call to shopify to find parent ID
    - Add ID to data
    - Once we have ID, sku, button link and URL
    - Loop through each data and make shopify call to upload and place under product meta
