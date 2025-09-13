#!/bin/bash
INPUT="$1"
DOWNLOAD_DIR="./pdfs"
mkdir -p "$DOWNLOAD_DIR"

while IFS=$'\t' read -r sku url; do
  [ "$sku" = "SKU" ] && continue   # skip header
  filename="$DOWNLOAD_DIR/${sku}_$(basename "$url")"
  [ -f "$filename" ] && echo "Skipping $filename" && continue
  echo "Downloading $url to $filename"
  curl -sSL "$url" -o "$filename"
done < "$INPUT"
