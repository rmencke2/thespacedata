"""
Django settings for myproject.

Works locally and on AWS Elastic Beanstalk.

- DEBUG controlled by env (default False)
- ALLOWED_HOSTS & CSRF_TRUSTED_ORIGINS from env, with safe defaults
- WhiteNoise serves static files (you can move to S3/CloudFront later)
"""

from pathlib import Path
import os

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me-for-local-only")

# DEBUG: False by default. Set DEBUG=true in env for local dev on EB if needed.
# --- Host & security settings -----------------------------------------------
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

# ---- Hosts -------------------------------------------------------------------
# If ALLOWED_HOSTS env is set, it wins (comma-separated).
# Otherwise allow localhost plus your EB CNAME (add your custom domain later).
_env_hosts = os.getenv("ALLOWED_HOSTS", "")
if _env_hosts.strip():
    ALLOWED_HOSTS = [h.strip() for h in _env_hosts.split(",") if h.strip()]
else:
     ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1", ".elasticbeanstalk.com"]


# CSRF: trust the public origins (scheme + host). If env set, it wins.
# Trust these origins for CSRF. (Include EB and your custom domains.)
_env_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if _env_csrf.strip():
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _env_csrf.split(",") if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        # Add your domains here as needed:
        "https://thespacedata-env.eba-2hmzdqix.us-east-1.elasticbeanstalk.com",
        # "https://yourdomain.com", "https://www.yourdomain.com",
    ]

# Behind ALB/App Runner so Django knows original scheme
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# One boolean to control HTTPS behavior (default ON in prod)
SECURE_SSL_REDIRECT = (
    os.getenv("SECURE_SSL_REDIRECT", "true").lower() in ("1", "true", "yes")
    and not DEBUG
)

# App Runner health check must stay HTTP
SECURE_REDIRECT_EXEMPT = [r"^health/?$"]

# Cookies track the same setting
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT

# HSTS only when we’re actually forcing HTTPS
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 60 * 60 * 24  # 1 day starter; raise later
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    SECURE_HSTS_SECONDS = 0
# -----------------------------------------------------------------------------
# OpenAI API (used by your generators)
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your apps
    "color_picker",
    "logo_generator",
    "name_generator",
    "users",
]

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: serve static files on EB & locally
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

# -----------------------------------------------------------------------------
# Database (SQLite for now; swap to RDS/Postgres later)
# -----------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static & Media
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]  # optional (for site.css etc.)

# Django 5 storage config (STATICFILES_STORAGE is removed)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------------------------------------------------
# Default PK
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------------------
# Logging (simple console)
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}