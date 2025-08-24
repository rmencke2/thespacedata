FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# System deps for psycopg2 (Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Collect static files (safe if none exist yet)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8080

# Start the app
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8080"]