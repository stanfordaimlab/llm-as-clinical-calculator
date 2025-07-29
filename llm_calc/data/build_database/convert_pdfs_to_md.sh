#!/bin/bash

# Directory containing condensed HTML files
HTML_DIR="data/build_database/reference_material/condensed_html"

# Directory to store generated markdown files
MD_DIR="data/build_database/reference_material/md"

# Create the markdown directory if it doesn't exist
mkdir -p "$MD_DIR"

# Loop through all HTML files in the HTML directory
for html_file in "$HTML_DIR"/*.html; do
    # Get the filename without extension
    filename=$(basename -- "$html_file")
    filename_no_ext="${filename%.*}"
    
    # Convert HTML to markdown using pandoc
    pandoc -s "$html_file" -o "$MD_DIR/$filename_no_ext.md"
    
    echo "Converted $filename to $filename_no_ext.md"
done

echo "Conversion complete. Markdown files are in $MD_DIR"
