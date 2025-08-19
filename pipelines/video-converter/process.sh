#!/bin/sh

# This is a placeholder script for a video converter.
# It simulates processing by printing the input filenames.

echo "--- Video Converter Pipeline (Simulation) ---"

if [ $# -eq 0 ]; then
    echo "No input files provided."
    exit 1
fi

echo "Received $# file(s) for 'conversion':"
echo ""

# Loop through all provided filenames
for file in "$@"
do
    echo "  -> $file"
done

echo ""
echo "Simulating a 5-second conversion process..."
sleep 5

echo ""
echo "--- Pipeline Finished ---"
