# Dockerfile (replace the whole file with this)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DJANGO_SETTINGS_MODULE=myproject.settings

WORKDIR /app

# System deps (psycopg2 etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code
COPY . .

# Collect static (ok if none)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8080

# Start Gunicorn (keep this on ONE line)
CMD ["gunicorn","myproject.wsgi:application","--bind","0.0.0.0:8080","--workers","2","--timeout","60"]