"""
Example Django settings snippets to integrate `ip_tracking` app.

Add the following to your project's `settings.py`:

INSTALLED_APPS += [
    'ip_tracking',
]

MIDDLEWARE += [
    'ip_tracking.middleware.IPTrackingMiddleware',
]

# django-ratelimit config (uses Django cache)
RATELIMIT_USE_CACHE = 'default'

# Celery beat example to run anomaly detection hourly
CELERY_BEAT_SCHEDULE = {
    'ip_tracking.detect_suspicious_ips_hourly': {
        'task': 'ip_tracking.tasks.detect_suspicious_ips',
        'schedule': 3600.0,  # every hour
    },
}

# Cache (example local-memory cache; in production use Redis/Memcached)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

"""
