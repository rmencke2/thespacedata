#!/usr/bin/env bash
set -euo pipefail

echo "Running entrypoint.sh..."

# Run migrations (safe in container start)
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn myproject.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --threads 4 \
    --timeout 120