#!/bin/bash
set -e  # Exit on error

echo "🔹 Updating pip..."
pip install --upgrade pip

echo "🔹 Installing dependencies from requirements.txt..."
pip install -r requirements.txt  # If this contains most dependencies, keep it

echo "🔹 Installing additional dependencies..."
pip install \
    astral pandasql requests-cache retry-requests numpy pandas \
    openpyxl holidays requests-ratelimiter matplotlib seaborn \
    scipy requests openmeteo_requests pytz pickle scikit-learn \
    IPython base64 json urllib3

echo "🔹 Installing Jupyter kernel..."
python -m ipykernel install --user --name=python3
