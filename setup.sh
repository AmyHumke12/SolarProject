#!/bin/bash
set -e  # Exit on error

echo "🔹 Updating pip..."
pip install --upgrade pip

echo "🔹 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "🔹 Installing additional dependencies..."
pip install \
    matplotlib seaborn scipy requests holidays requests_cache \
    pandasql pytz numpy pickle scikit-learn IPython requests_ratelimiter \
    urllib3 base64 json openmeteo_requests

echo "🔹 Installing Jupyter kernel..."
python -m ipykernel install --user --name=python3
