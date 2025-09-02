#!/usr/bin/env bash
# Be careful with -e here; we want the server to start even if a prep step fails.
set -o pipefail

# Default port for App Runner
PORT="${PORT:-8080}"
WORKERS="${WEB_CONCURRENCY:-2}"
TIMEOUT="${WEB_TIMEOUT:-120}"

echo "[entrypoint] collectstatic…"
python manage.py collectstatic --noinput || echo "[entrypoint] collectstatic failed (continuing)"

echo "[entrypoint] migrate…"
python manage.py migrate --noinput || echo "[entrypoint] migrate failed (continuing)"

echo "[entrypoint] starting gunicorn on 0.0.0.0:${PORT}…"
exec gunicorn myproject.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WORKERS}" \
  --timeout "${TIMEOUT}" \
  --access-logfile '-' \
  --error-logfile '-'