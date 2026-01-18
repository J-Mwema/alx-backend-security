from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

from .models import RequestLog, SuspiciousIP


@shared_task
def detect_suspicious_ips():
    """Hourly task to detect suspicious IPs.

    Flags IPs that:
    - made more than 100 requests in the last hour
    - accessed sensitive paths like /admin or /login
    """
    now = timezone.now()
    window = now - timedelta(hours=1)

    # 1) High request volume
    heavy_qs = (
        RequestLog.objects
        .filter(timestamp__gte=window)
        .values('ip_address')
        .annotate(count=Count('id'))
        .filter(count__gt=100)
    )

    for row in heavy_qs:
        ip = row['ip_address']
        reason = f"{row['count']} requests in last hour"
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason=reason)

    # 2) Sensitive path access
    sensitive = ['/admin', '/login']
    sens_qs = (
        RequestLog.objects
        .filter(timestamp__gte=window, path__in=sensitive)
        .values('ip_address')
        .annotate(count=Count('id'))
    )

    for row in sens_qs:
        ip = row['ip_address']
        reason = f"accessed sensitive path(s) ({row['count']} hits)"
        SuspiciousIP.objects.get_or_create(ip_address=ip, reason=reason)
