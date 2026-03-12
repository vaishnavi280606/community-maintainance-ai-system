#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('vader_lexicon', quiet=True); nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)"

echo "Collecting static files..."
cd backend
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding data..."
python manage.py seed_data || echo "Seed data already exists or skipped"

echo "Build complete!"
