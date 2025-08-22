# Python slim base
FROM python:3.11-slim

# Good defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir inside the image
WORKDIR /app

# System packages needed for psycopg2 etc.
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# ---- Install Python deps (cache-friendly layer) ----
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- Copy app source ----
COPY . .

# ---- Static files ----
# Tell Django exactly where STATIC_ROOT is and ensure it exists
ENV DJANGO_STATIC_ROOT=/app/staticfiles
RUN mkdir -p /app/staticfiles
# Collect static assets
RUN python manage.py collectstatic --noinput

# App Runner/containers use this port
EXPOSE 8000

# ---- Start server ----
# (If you later add an entrypoint that runs migrations, replace this CMD.)
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]