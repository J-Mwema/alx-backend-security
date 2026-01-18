from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import requests

from .models import RequestLog, BlockedIP


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '0.0.0.0'


class IPTrackingMiddleware(MiddlewareMixin):
    """Middleware that logs requests, blocks blacklisted IPs and enriches with geo data."""

    BLOCKED_IP_CACHE_KEY = 'ip_tracking:blocked_ip:'
    GEO_CACHE_KEY = 'ip_tracking:geo:'
    BLOCKED_CACHE_TIMEOUT = 60 * 5  # 5 minutes
    GEO_CACHE_TIMEOUT = 24 * 60 * 60  # 24 hours

    def process_request(self, request):
        ip = get_client_ip(request)

        # Check blacklist (cached)
        if self._is_ip_blocked(ip):
            # Log blocked attempt and return 403
            try:
                RequestLog.objects.create(
                    ip_address=ip,
                    timestamp=timezone.now(),
                    path=request.path,
                    method=request.method,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255] or None,
                )
            except Exception:
                pass
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')

        # Build basic log data
        path = request.path
        method = request.method
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255] or None

        # Get geolocation (cached)
        country = city = None
        geo = cache.get(f"{self.GEO_CACHE_KEY}{ip}")
        if geo is None:
            geo = self._fetch_geolocation(ip)
            if geo:
                cache.set(f"{self.GEO_CACHE_KEY}{ip}", geo, self.GEO_CACHE_TIMEOUT)

        if geo:
            country = geo.get('country')
            city = geo.get('city')

        # Persist request log
        try:
            RequestLog.objects.create(
                ip_address=ip,
                timestamp=timezone.now(),
                path=path,
                method=method,
                user_agent=user_agent,
                country=country,
                city=city,
            )
        except Exception:
            pass

        return None

    def _is_ip_blocked(self, ip):
        cache_key = f"{self.BLOCKED_IP_CACHE_KEY}{ip}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached is True

        try:
            now = timezone.now()
            blocked = BlockedIP.objects.filter(ip_address=ip, is_active=True).exclude(expires_at__lt=now).exists()
        except Exception:
            # fail open
            blocked = False

        cache.set(cache_key, blocked, self.BLOCKED_CACHE_TIMEOUT)
        return blocked

    def _fetch_geolocation(self, ip):
        """Fetch a simple geolocation for the IP.

        Uses a public IP geolocation service (ipapi.co). Results are cached.
        """
        try:
            resp = requests.get(f'https://ipapi.co/{ip}/json/', timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                return {'country': data.get('country_name'), 'city': data.get('city')}
        except Exception:
            return None
        return None
