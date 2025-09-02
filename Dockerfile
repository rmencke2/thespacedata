# ---------- build/run stage ----------
    FROM python:3.12-slim AS app

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1 \
        DJANGO_SETTINGS_MODULE=myproject.settings
    
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
    
    ## --- runtime config ---
    WORKDIR /app

    # copy entrypoint and make it executable
    COPY entrypoint.sh /app/entrypoint.sh
    RUN chmod +x /app/entrypoint.sh

    # App Runner’s default health-check port
    ENV PORT=8080
    EXPOSE 8080

    # start the app via entrypoint
    CMD ["/app/entrypoint.sh"]