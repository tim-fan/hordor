import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from inventory.models import Photo


class Command(BaseCommand):
    help = (
        "Delete image files under MEDIA_ROOT/images that aren't referenced "
        "by any Photo. Safe by default (reports only) -- pass --delete to "
        "actually remove files."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help="Actually delete orphaned files (default: report only).",
        )
        parser.add_argument(
            '--min-age-hours',
            type=float,
            default=24,
            help="Skip files modified more recently than this, in case an "
                 "upload is still in progress (default: 24).",
        )

    def handle(self, *args, **options):
        images_dir = Path(settings.MEDIA_ROOT) / 'images'

        referenced = set()
        for photo in Photo.objects.all():
            if photo.image:
                referenced.add(photo.image.name)

        min_age_seconds = options['min_age_hours'] * 3600
        now = time.time()

        orphans = []
        for path in images_dir.iterdir():
            if not path.is_file():
                continue
            rel_name = f'images/{path.name}'
            if rel_name in referenced:
                continue
            if now - path.stat().st_mtime < min_age_seconds:
                continue
            orphans.append(path)

        total_size = sum(p.stat().st_size for p in orphans)
        prefix = '' if options['delete'] else '[DRY RUN] '
        self.stdout.write(f"{prefix}Found {len(orphans)} orphaned files, {total_size / 1e6:.1f} MB")

        if options['delete']:
            for path in orphans:
                path.unlink()
            self.stdout.write(f"Deleted {len(orphans)} files, freed {total_size / 1e6:.1f} MB")
        elif orphans:
            self.stdout.write("Re-run with --delete to remove these.")
