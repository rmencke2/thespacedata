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
    #COPY requirements.txt /app/requirements.txt
    #RUN pip install -r /app/requirements.txt
        
    # Make sure gunicorn & whitenoise are installed (add if not in requirements.txt)
    RUN pip install gunicorn whitenoise
    
    # Copy project
    COPY . /app
    
    # Make sure we’re in /app
    WORKDIR /app

    # 1) Copy requirements and install from the SAME path
    COPY requirements.txt .
    RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

    # 2) Copy the rest of the project into the image
    COPY . .

    # 3) Copy entrypoint and make it executable
    COPY entrypoint.sh /app/entrypoint.sh
    RUN chmod +x /app/entrypoint.sh

    # 4) App Runner defaults to 8080; we’ll use it
    ENV PORT=8080
    EXPOSE 8080

    # 5) Start the container with our script
    CMD ["/app/entrypoint.sh"]