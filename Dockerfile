# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DJANGO_SETTINGS_MODULE=myproject.settings

WORKDIR /app

# --- system deps for Pillow/CairoSVG/png/svg text rendering ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev libpng-dev libfreetype6-dev \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 librsvg2-2 \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code
COPY . .

# A writeable media dir (good for App Runner)
RUN mkdir -p /tmp/media

# Collect static (ignore if none)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8080
CMD ["bash","-lc","gunicorn myproject.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120"]