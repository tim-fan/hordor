"""
Settings for the LAN-facing container: same code, database and media as
production, but served over plain HTTP directly on the home network
(bypassing the Cloudflare tunnel and its upload-speed bottleneck).

The HTTPS-only hardening from production.py is switched off here because
there is no TLS terminator in front of this instance. That is only
acceptable because the port is reachable from the home LAN alone --
never expose this configuration to the internet.
"""
from hordor.settings.production import *

# Comma-separated, e.g. HORDOR_LAN_HOSTS=192.168.1.20,myhost.local
# An mDNS (.local) name survives IP reallocation; a raw IP is a useful
# fallback for clients without mDNS. Set in hordor_secrets.lan.env,
# which stays outside the repo along with the rest of the
# instance-specific config.
HORDOR_LAN_HOSTS = [h.strip() for h in os.environ['HORDOR_LAN_HOSTS'].split(',') if h.strip()]

ALLOWED_HOSTS = HORDOR_LAN_HOSTS
CSRF_TRUSTED_ORIGINS = [f'http://{h}:8001' for h in HORDOR_LAN_HOSTS]

SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
