"""
Django settings for the faq_chatbot project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env on the local computer
load_dotenv(BASE_DIR / ".env")


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in ("1", "true", "yes", "on")


# --------------------------------------------------
# Security
# --------------------------------------------------

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    "insecure-dev-key-change-me"
)

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

if os.environ.get("DJANGO_ALLOWED_HOSTS"):
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
        if host.strip()
    )


# --------------------------------------------------
# Applications
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chatbot",
]


# --------------------------------------------------
# Middleware
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "faq_chatbot.urls"


# --------------------------------------------------
# Templates
# --------------------------------------------------

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


WSGI_APPLICATION = "faq_chatbot.wsgi.application"


# --------------------------------------------------
# Database
# --------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "faq_chatbot"),
        "USER": env("DB_USER", "postgres"),
        "PASSWORD": env("DB_PASSWORD", ""),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}


# --------------------------------------------------
# Password validation
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# --------------------------------------------------
# Internationalization
# --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# Static files
# --------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# --------------------------------------------------
# Authentication
# --------------------------------------------------

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "chat_page"
LOGOUT_REDIRECT_URL = "login"


# --------------------------------------------------
# Default primary key
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"