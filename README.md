# alx-backend-security

This repository contains an `ip_tracking` Django app that provides:

- IP request logging (`RequestLog`)
- IP blacklist (`BlockedIP`) and management command to add blocks
- Geolocation enrichment (country, city) cached for 24 hours
- Rate-limited example login view using `django-ratelimit`
- Hourly Celery task that flags suspicious IPs (`SuspiciousIP`)

See `example_settings.py` for suggested `settings.py` changes.
