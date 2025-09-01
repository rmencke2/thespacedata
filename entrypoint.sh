#!/usr/bin/env bash
set -euo pipefail

# Optional: make logs unbuffered for nicer App Runner logs
export PYTHONUNBUFFERED=1

# Sanity: ensure we’re in /app
cd /app

echo "[entrypoint] Running migrations…"
python manage.py migrate --noinput

echo "[entrypoint] Collecting static…"
python manage.py collectstatic --noinput

echo "[entrypoint] Starting gunicorn…"
# Bind to 8080 because your App Runner health check hits port 8080
exec gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile '-' --error-logfile '-'