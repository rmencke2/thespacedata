#!/usr/bin/env bash
set -e

# Optional: database migrations (won’t fail deploy if no DB changes)
python manage.py migrate --noinput || true

# Optional: collect static (safe to repeat; uses STATIC_ROOT)
python manage.py collectstatic --noinput || true

# Start Gunicorn on the port App Runner expects
exec gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile '-' \
  --error-logfile '-'