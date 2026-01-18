# alx-backend-security

This repository contains an `ip_tracking` Django app that provides:

- IP request logging (`RequestLog`)
- IP blacklist (`BlockedIP`) and a management command to add/update blocks
- Geolocation enrichment (country, city) cached for 24 hours
- Rate-limited example login view using `django-ratelimit`
- Hourly Celery task that flags suspicious IPs (`SuspiciousIP`)

Quick start
-----------

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure `settings.py` in the repo root is merged into your Django project's settings. The provided `settings.py` is a minimal example that registers the `ip_tracking` app and middleware.

3. Apply migrations and run the server:

```bash
python manage.py makemigrations ip_tracking
python manage.py migrate
python manage.py runserver
```

4. Block an IP via management command:

```bash
python manage.py block_ip 1.2.3.4 --reason "malicious" --days 7
```

5. Start Celery worker + beat to enable hourly anomaly detection (requires Redis or other broker):

```bash
celery -A your_project_name worker -l info
celery -A your_project_name beat -l info
```

Notes
-----

- Middleware: `ip_tracking.middleware.IPTrackingMiddleware` logs requests and blocks IPs present in `BlockedIP`.
- Geolocation: middleware uses `ipapi.co` (via `requests`) and caches results for 24 hours. Swap provider if desired.
- Rate limiting: example `login_view` in `ip_tracking/views.py` uses `django-ratelimit` (configured in `requirements.txt`). Adjust rates in the view decorators.
- Settings: integrate the minimal `settings.py` into your real project settings; do not run production with `DEBUG=True`.

Files of interest
-----------------

- `ip_tracking/models.py` — `RequestLog`, `BlockedIP`, `SuspiciousIP`
- `ip_tracking/middleware.py` — request logging, blocking, geo enrichment
- `ip_tracking/management/commands/block_ip.py` — CLI to add blocked IPs
- `ip_tracking/views.py` — rate-limited example login view
- `ip_tracking/tasks.py` — Celery task `detect_suspicious_ips`
- `requirements.txt` — packages used
