FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=myproject.settings

WORKDIR /app

# If you don't use Postgres, you can drop libpq-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (fail if broken so you catch it at build time)
RUN python manage.py collectstatic --noinput

# EB reverse proxy expects 8080; App Runner passes $PORT which we honor below
EXPOSE 8080

# Helpful logging flags for EB/App Runner
# Bind to $PORT if set (App Runner), else 8080 (EB)
CMD ["bash", "-lc", "gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -"]