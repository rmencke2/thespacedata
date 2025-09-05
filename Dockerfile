# ---- base ----
  FROM python:3.11-slim AS base
  ENV PYTHONDONTWRITEBYTECODE=1 \
      PYTHONUNBUFFERED=1 \
      PIP_NO_CACHE_DIR=1
  
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl && \
      rm -rf /var/lib/apt/lists/*
  
  WORKDIR /app
  
  # ---- deps ----
  COPY requirements.txt .
  RUN python -m pip install --upgrade pip && pip install -r requirements.txt
  
  # ---- app ----
  COPY . .
  
  # Collect static at build-time so runtime is instant.
  # IMPORTANT: make sure your settings work with USE_S3=false for builds.
  ENV DJANGO_SETTINGS_MODULE=myproject.settings \
      USE_S3=false
  RUN python manage.py collectstatic --noinput
  
  # ---- run ----
  EXPOSE 8080
  # Gunicorn must bind 0.0.0.0:$PORT for App Runner
  CMD ["gunicorn","myproject.wsgi:application","--bind","0.0.0.0:8080","--workers","2","--threads","8","--timeout","60"]