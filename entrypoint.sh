#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<unset>}"
echo "[entrypoint] DEBUG=${DJANGO_DEBUG:-<unset>}"
echo "[entrypoint] Collecting static & migrating…"

# SQLite lives in /tmp (writable on App Runner)
mkdir -p /tmp /tmp/media /tmp/staticfiles

# Best-effort migrations; if you want hard-fail, remove `|| true`
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

echo "[entrypoint] Starting gunicorn…"
exec gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 90 \
  --access-logfile - \
  --error-logfile -