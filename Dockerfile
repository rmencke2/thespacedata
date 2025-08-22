FROM python:3.11-slim

WORKDIR /app

# system deps for psycopg2 etc.
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static (will use STATIC_ROOT)
RUN python manage.py collectstatic --noinput

# Gunicorn server
ENV PORT=8000
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
