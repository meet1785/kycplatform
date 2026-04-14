from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Use local file storage in development
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Django Debug Toolbar (optional)
INSTALLED_APPS += ["django.contrib.staticfiles"]  # noqa

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
