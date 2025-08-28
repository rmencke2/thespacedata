# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DJANGO_SETTINGS_MODULE=myproject.settings   # <-- set your project package

WORKDIR /app

# (Optional) system libs you need (Pillow needs libjpeg/zlib, psycopg2 needs libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make sure requirements.txt includes: django, gunicorn, pillow, psycopg2-binary (or libpq+psycopg)
# gunicorn is REQUIRED in prod.

COPY . .

# Collect static (won’t fail the build if none yet)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8080

# Use the correct WSGI module path
# myproject.wsgi:application  <- change "myproject" if yours is different
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60"]