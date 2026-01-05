#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations if database is configured
if [ -n "$DATABASE_URL" ] || [ -n "$DB_HOST" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
else
    echo "WARNING: No database configured. Skipping migrations."
    echo "Set DATABASE_URL or DB_* environment variables and run 'python manage.py migrate' manually."
fi
