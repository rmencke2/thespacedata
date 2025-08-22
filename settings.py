from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# allow build without leaking debug
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # <— this is required for collectstatic