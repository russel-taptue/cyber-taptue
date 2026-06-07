from .base import *

DEBUG = False

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

EMAIL_TIMEOUT = 15

if env("SENDGRID_API_KEY", default=None):
    EMAIL_HOST = "smtp.sendgrid.net"
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "apikey"
    EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY")
    EMAIL_USE_TLS = True

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", default="https://cyberwithtaptue.com").split(",")

if env("DATABASE_URL", default=None):
    DATABASES = {"default": env.db()}

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
