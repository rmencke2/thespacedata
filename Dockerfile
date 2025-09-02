# ---------- build/run stage ----------
    FROM python:3.12-slim AS app

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1 \
        DJANGO_SETTINGS_MODULE=myproject.settings
    
    WORKDIR /app
    
    # System deps you might need for pip wheels (adjust as your deps require)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
      && rm -rf /var/lib/apt/lists/*
    
    # Copy only requirements first for better layer caching
    COPY requirements.txt /app/requirements.txt
    RUN pip install -r requirements.txt
    
    # Make sure gunicorn & whitenoise are installed (add if not in requirements.txt)
    RUN pip install gunicorn whitenoise
    
    # Copy project
    COPY . /app
    
    # Copy the root entrypoint (NOT docker/entrypoint.sh)
    COPY entrypoint.sh /app/entrypoint.sh
    RUN chmod +x /app/entrypoint.sh
    CMD ["/app/entrypoint.sh"]
    
    # Expose the port App Runner hits
    ENV PORT=8080
    EXPOSE 8080
    
    # One entrypoint only (no extra CMDs elsewhere)
    ENTRYPOINT ["/entrypoint.sh"]