#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<unset>}"
echo "[entrypoint] DEBUG=${DJANGO_DEBUG:-<unset>}"
echo "[entrypoint] DATABASE_URL=${DATABASE_URL:+<set>}${DATABASE_URL:-<unset - using SQLite>}"

# Create directories for local storage (fallback)
mkdir -p /tmp /tmp/media /tmp/staticfiles

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput || true

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput || true

echo "[entrypoint] Starting gunicorn…"
exec gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -