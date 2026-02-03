#!/bin/bash

# Configuration
ENV_NAME="paper_agg"

echo "Using Conda environment: $ENV_NAME"

# Function to run command in conda env
run_in_env() {
    conda run -n "$ENV_NAME" --no-capture-output "$@"
}

# Run the scanner first if DB is missing (optional, but good for first run)
if [ ! -f database/papers.db ]; then
    echo "Initializing database and running first scan..."
    run_in_env python scanner.py
fi

echo "Starting Paper Aggregator Server..."
echo "Open http://localhost:8000 in your browser."

# Run uvicorn via python module to ensure correct path resolution
run_in_env python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
