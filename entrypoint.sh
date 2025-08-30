#!/usr/bin/env bash
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn myproject.wsgi:application --bind 0.0.0.0:8080 --workers 2 --timeout 120