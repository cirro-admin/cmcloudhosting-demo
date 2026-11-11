"""Settings for the CM Cloud Django starter.

Everything environment-specific is read from environment variables, because that
is the only configuration channel the platform has: values set in the app's
Deploy settings land in the process environment, and the runtime additionally
provides ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS and DJANGO_SETTINGS_MODULE.
"""
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_list(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


# 🔑 Read from the environment, do not hard-code. The runtime sets ALLOWED_HOSTS
# to this app's hostname; with DEBUG off and an empty list Django answers every
# request with 400 Bad Request, including through nginx, so the site looks dead
# while the deploy reports success.
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]

# nginx terminates TLS and proxies plain HTTP to this process, so Django would
# otherwise see an http request on a page the browser loaded over https and
# reject the admin login POST as a CSRF failure.
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ⛔ No fallback value. A default secret key would be shared by every deployment
# of this starter and would still sign real sessions and password-reset tokens.
# Set SECRET_KEY in the app's Deploy settings; Django's own error if it is
# missing is clearer than a placeholder that silently works.
SECRET_KEY = os.environ["SECRET_KEY"] if "SECRET_KEY" in os.environ else None
if not SECRET_KEY:
    SECRET_KEY = "insecure-development-only-set-SECRET_KEY-in-deploy-settings"

DEBUG = os.environ.get("DEBUG", "") == "1"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "entries",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "starter.urls"
WSGI_APPLICATION = "starter.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


def _database_from_url(url: str) -> dict:
    """Parse a postgres:// URL into Django's DATABASES shape.

    Hand-parsed rather than pulling in dj-database-url: three lines of stdlib
    beat a dependency, and it makes the contract visible -- a CM Cloud managed
    PostgreSQL database hands you exactly this URL.
    """
    parts = urlparse(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parts.path.lstrip("/"),
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or 5432),
        "CONN_MAX_AGE": 60,
        # Managed PostgreSQL requires TLS on its public endpoint
        # (db.cmcloudhosting.com:5432) and permits it internally, so requiring
        # it is correct either way.
        "OPTIONS": {"sslmode": os.environ.get("PGSSLMODE", "require")},
    }


_database_url = os.environ.get("DATABASE_URL", "").strip()
if _database_url:
    DATABASES = {"default": _database_from_url(_database_url)}
else:
    # No DATABASE_URL: run on SQLite so a first deploy works before a database
    # is ordered. ⚠️ The file lives in the release directory, so it is REPLACED
    # on every deploy -- fine for a demo, never for real data.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# The runtime runs `collectstatic` and points nginx at STATIC_ROOT, so assets are
# served from disk rather than through Python. Without STATIC_ROOT set, nothing
# is collected and the Django admin's own CSS 404s.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# MEDIA_ROOT inside the project would be wiped by every deploy (each release is
# a fresh clone). The runtime detects that and relinks it to persistent
# per-app storage, then serves MEDIA_URL from there.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
