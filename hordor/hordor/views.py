from django.contrib.auth.decorators import login_required
from django.views.static import serve


# serve media password protected, as per:
# https://blog.majsky.cz/django-protected-media-files/
@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    response = serve(request, path, document_root, show_indexes)
    # 'private' forbids shared caches (Cloudflare's edge) from storing these
    # -- otherwise a cached copy is served to anyone with the URL, without
    # the login check ever running. Browsers may still cache locally.
    response['Cache-Control'] = 'private, max-age=3600'
    return response
