from django.http import JsonResponse
from ratelimit.decorators import ratelimit


@ratelimit(key='ip', rate='10/m', method=['POST'], block=True)
def _login_authenticated(request):
    return JsonResponse({'status': 'ok', 'message': 'authenticated login endpoint'})


@ratelimit(key='ip', rate='5/m', method=['POST'], block=True)
def _login_anonymous(request):
    return JsonResponse({'status': 'ok', 'message': 'anonymous login endpoint'})


def login_view(request):
    """Example sensitive view (login) with IP-based rate limiting.

    POST requests are rate-limited differently depending on authentication state.
    """
    if request.user and request.user.is_authenticated:
        return _login_authenticated(request)
    return _login_anonymous(request)
