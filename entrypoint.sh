#!/usr/bin/env bash
set -e

# Optional: show Python / Django versions in logs for debugging
python -V
python -c "import django, sys; print('Django', django.get_version())" || true

# Run DB migrations (won’t hurt on SQLite)
python manage.py migrate --noinput

# Start Gunicorn, pointing to the CORRECT module path
# (your project is named "myproject", so the WSGI callable is myproject.wsgi:application)
exec gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers 3 \
  --timeout 120
