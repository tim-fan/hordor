from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from .models import ShareLink

SHARE_VIEWER_USERNAME = 'shared_viewer'


def _get_share_viewer():
    viewer, _ = User.objects.get_or_create(username=SHARE_VIEWER_USERNAME)
    if viewer.has_usable_password():
        viewer.set_unusable_password()
        viewer.save(update_fields=['password'])
    return viewer


class ReadOnlyShareMiddleware:
    """
    Recognizes the dedicated read-only viewer account (logged in via
    share_login_view). Re-checks the ShareLink backing the session on
    every request -- deleting/expiring the ShareLink row revokes access
    immediately, rather than waiting out the session's cookie lifetime.
    Blocks all non-GET/HEAD requests as a hard backstop regardless of
    what the UI shows.

    Also accepts ?share_token=<token> on GET/HEAD requests as a
    stateless, cookie-free variant of the same access, for clients that
    can't hold a session (e.g. simple URL-fetch tools). Authenticates
    that single request only; nothing is written to any session.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_readonly_visitor = False

        if request.user.is_authenticated and request.user.username == SHARE_VIEWER_USERNAME:
            token = request.session.get('share_token')
            link = ShareLink.objects.filter(token=token).first() if token else None
            if link is None or link.is_expired():
                logout(request)
            else:
                request.is_readonly_visitor = True
                # /accounts/ (login, logout) stays POSTable, so a read-only
                # session can always be escaped by logging out or logging in
                # as a real user.
                if request.method not in ('GET', 'HEAD') and not request.path.startswith('/accounts/'):
                    return HttpResponseForbidden("This is a read-only shared view.")
        elif not request.user.is_authenticated and request.method in ('GET', 'HEAD'):
            token = request.GET.get('share_token')
            link = ShareLink.objects.filter(token=token).first() if token else None
            if link is not None and not link.is_expired():
                request.user = _get_share_viewer()
                request.is_readonly_visitor = True

        return self.get_response(request)
