from datetime import timedelta

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from inventory.models import ShareLink


class Command(BaseCommand):
    help = "Create a read-only share link for friends, valid for --days (default 30)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help="Days until the link expires (default: 30).",
        )

    def handle(self, *args, **options):
        link = ShareLink.objects.create(
            expires_at=timezone.now() + timedelta(days=options['days']),
        )
        path = reverse('inventory:share_login', kwargs={'token': link.token})
        self.stdout.write(f"Share link expires {link.expires_at:%Y-%m-%d}. Prepend your domain to:")
        self.stdout.write(path)
