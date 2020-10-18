from django.contrib.auth.decorators import login_required
from django.views.static import serve


# serve media password protected, as per:
# https://blog.majsky.cz/django-protected-media-files/
@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)