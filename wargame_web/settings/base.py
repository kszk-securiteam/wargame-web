import os
import yaml
from django.contrib import messages
from djangocodemirror.settings import *

with open(os.getenv("CONFIG_FILE", "config.yaml"), "r") as f:
    YAML_SETTINGS = yaml.safe_load(f)

DEBUG = YAML_SETTINGS.get("debug")
SECRET_KEY = YAML_SETTINGS.get("secret_key")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = YAML_SETTINGS.get("allowed_hosts")


ASGI_APPLICATION = "wargame_web.routing.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": {"hosts": [("127.0.0.1", 6379)]}}
}

DATA_UPLOAD_MAX_MEMORY_SIZE = None

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bootstrap4",
    "wargame",
    "markdownx",
    "wargame_admin",
    "django_registration",
    "chunked_upload",
    "djangocodemirror",
    "taggit",
    "channels",
    "django_filters",
    "bootstrap_pagination",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wargame_web.middleware.DisableSiteMiddleware",
    "wargame_web.middleware.RequireEmailMiddleware",
]

ROOT_URLCONF = "wargame_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "wargame_web.wsgi.application"

AUTH_PASSWORD_VALIDATORS = []

FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Substitute user model with our own
AUTH_USER_MODEL = "wargame.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
APPEND_SLASH = True
MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"

MESSAGE_TAGS = {
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

EMAIL_HOST = YAML_SETTINGS.get("email").get("host")
EMAIL_PORT = YAML_SETTINGS.get("email").get("port")
EMAIL_USE_SSL = YAML_SETTINGS.get("email").get("use_ssl")
EMAIL_HOST_USER = YAML_SETTINGS.get("email").get("user")
EMAIL_HOST_PASSWORD = YAML_SETTINGS.get("email").get("password")
EMAIL_FROM = YAML_SETTINGS.get("email").get("from")

TAGGIT_CASE_INSENSITIVE = True
