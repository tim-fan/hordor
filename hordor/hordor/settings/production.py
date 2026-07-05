import os
from hordor.settings.common import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

# Set in hordor_secrets.env alongside SECRET_KEY, e.g. HORDOR_DOMAIN=hordor.yourdomain.com
HORDOR_DOMAIN = os.environ['HORDOR_DOMAIN']

ALLOWED_HOSTS = [HORDOR_DOMAIN]
CSRF_TRUSTED_ORIGINS = [f'https://{HORDOR_DOMAIN}']

# Cloudflare terminates TLS at its edge; cloudflared forwards the original
# request scheme to the origin (over plain HTTP inside the tunnel) via this
# header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Not enabling SECURE_HSTS_SECONDS yet -- browsers cache HSTS aggressively, so
# it's worth turning on only after confirming HTTPS is solid via the tunnel.

MIDDLEWARE = MIDDLEWARE.copy()
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
