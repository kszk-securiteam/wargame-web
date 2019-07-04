from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": YAML_SETTINGS.get("database").get("name"),
        "USER": YAML_SETTINGS.get("database").get("user"),
        "PASSWORD": YAML_SETTINGS.get("database").get("password"),
        "HOST": YAML_SETTINGS.get("database").get("host"),
        "PORT": YAML_SETTINGS.get("database").get("port"),
    }
}

X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
