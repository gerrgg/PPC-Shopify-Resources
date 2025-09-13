for f in ./pdfs/*.pdf; do
  file "$f" | grep -q 'PDF document' || echo "Warning: $f is not a PDF"
done
