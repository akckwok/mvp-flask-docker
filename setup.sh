#!/bin/bash

# Exit on any error
set -e

echo "--- Starting Project Setup ---"

# --- Prerequisite Checks ---
echo "1. Checking for prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo >&2 "Python 3 is not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "npm is not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Aborting."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo >&2 "jq is not installed. Aborting."; exit 1; }
echo "All prerequisites found."

# --- Backend Setup ---
echo "2. Installing Python dependencies..."
pip install -r requirements.txt
echo "Python dependencies installed."

# --- Frontend Setup ---
echo "3. Installing frontend dependencies..."
npm install --prefix dashboard-ui
echo "Frontend dependencies installed."

# --- Build Pipeline Images ---
echo "4. Building pipeline Docker images..."
for pipeline in pipelines/*/; do
    if [ -f "$pipeline/manifest.json" ]; then
        pipeline_id=$(basename "$pipeline")
        image_name=$(jq -r '.image_name // ""' "$pipeline/manifest.json")
        if [ -z "$image_name" ]; then
            image_name="${pipeline_id}-image"
        fi
        echo "Building image '$image_name' for pipeline '$pipeline_id'..."
        docker build -t "$image_name" "$pipeline"
    fi
done
echo "Pipeline images built."

# --- Build Frontend ---
echo "5. Building frontend for production..."
npm run build --prefix dashboard-ui
echo "Frontend built."

echo "--- Setup Complete ---"
echo "You can now run the application in production mode with: python run.py"
