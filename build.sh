#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
# Explicitly fake the problematic migration first
python manage.py migrate gamerank_users 0002 --fake

# Now apply all other pending migrations
python manage.py migrate 