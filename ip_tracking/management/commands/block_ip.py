from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta

from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = 'Block an IP address'

    def add_arguments(self, parser):
        parser.add_argument('ip', help='IP address to block')
        parser.add_argument('--reason', help='Reason for blocking', default='')
        parser.add_argument('--days', type=int, help='Number of days until block expires', default=0)

    def handle(self, *args, **options):
        ip = options['ip']
        reason = options.get('reason') or ''
        days = options.get('days') or 0

        expires_at = None
        if days > 0:
            expires_at = timezone.now() + timedelta(days=days)

        obj, created = BlockedIP.objects.update_or_create(
            ip_address=ip,
            defaults={'reason': reason, 'is_active': True, 'expires_at': expires_at}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Blocked IP {ip}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated block for IP {ip}'))
