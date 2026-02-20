import os
from urllib.parse import urlparse

from .prod import *  # noqa: F401, F403

DEBUG = True

# Use SQLite for local testing unless DATABASE_URL is explicitly set
database_url = os.environ.get("DATABASE_URL")
if database_url:
    parsed = urlparse(database_url)
    DATABASES["default"] = {  # noqa: F405
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username,
        "PASSWORD": parsed.password,
        "HOST": parsed.hostname,
        "PORT": parsed.port or 5432,
    }
else:
    DATABASES["default"] = {  # noqa: F405
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]
