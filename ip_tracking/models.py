from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import ipaddress



from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """Stores an incoming request entry."""
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'

    def __str__(self):
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else 'n/a'
        return f"{self.ip_address} - {self.path} - {ts}"


class BlockedIP(models.Model):
    """IP addresses that are blocked from accessing the site."""
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'

    def __str__(self):
        return f"{self.ip_address} ({'active' if self.is_active else 'inactive'})"

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False


class SuspiciousIP(models.Model):
    """IPs flagged by anomaly detection."""
    ip_address = models.GenericIPAddressField(db_index=True)
    reason = models.CharField(max_length=255)
    flagged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-flagged_at']
        verbose_name = 'Suspicious IP'
        verbose_name_plural = 'Suspicious IPs'

    def __str__(self):
        return f"{self.ip_address} - {self.reason} at {self.flagged_at}"
