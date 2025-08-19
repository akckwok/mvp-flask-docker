#!/bin/sh

# This script runs inside the Docker container.
# It receives input filenames as command-line arguments.

echo "--- Word Counter Pipeline ---"

if [ $# -eq 0 ]; then
    echo "No input files provided."
    exit 1
fi

echo "Processing $# file(s)..."
echo ""

# Loop through all provided filenames
for file in "$@"
do
    # The files are expected to be in the /data directory
    filepath="/data/$file"
    if [ -f "$filepath" ]; then
        echo "--- Results for $file ---"
        wc "$filepath"
        echo ""
    else
        echo "Warning: File not found at $filepath"
    fi
done

echo "--- Pipeline Finished ---"
