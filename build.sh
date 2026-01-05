#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
# Disable database checks during collectstatic
export DJANGO_SETTINGS_MODULE=Task_Manager.settings
export DISABLE_SERVER_SIDE_CURSORS=1
python manage.py collectstatic --no-input --verbosity 0

# Run migrations only if database is configured
if [ -n "$DATABASE_URL" ] || [ -n "$DB_HOST" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "✓ Migrations completed successfully"
else
    echo "⚠ WARNING: No database configured. Skipping migrations."
    echo "To complete setup:"
    echo "1. Set DATABASE_URL (for PostgreSQL) OR DB_HOST, DB_NAME, DB_USER, DB_PASSWORD (for MySQL)"
    echo "2. Run: python manage.py migrate"
    echo "3. Run: python manage.py createsuperuser"
fi

echo "✓ Build completed successfully"
