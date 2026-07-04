import os

from django.core.management.base import BaseCommand

from inventory.imaging import as_jpg_name, compress_image_file
from inventory.models import Container, ItemPhoto


class Command(BaseCommand):
    help = (
        "Recompress all existing item/container photos in place to a "
        "size-capped JPEG (see inventory/imaging.py for the target "
        "dimension/quality). Only ever replaces a file with a smaller one."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Report projected savings without changing any files.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        field_files = [(photo, 'image') for photo in ItemPhoto.objects.all()]
        field_files += [
            (container, 'photo')
            for container in Container.objects.exclude(photo='').exclude(photo__isnull=True)
        ]

        total_before = 0
        total_after = 0
        processed = 0
        skipped_not_smaller = 0
        errors = 0

        for instance, field_name in field_files:
            field_file = getattr(instance, field_name)
            if not field_file:
                continue

            old_name = field_file.name
            try:
                field_file.open('rb')
                before_size = field_file.size
                compressed = compress_image_file(field_file)
            except Exception as exc:
                self.stderr.write(f"Skipping {old_name}: {exc}")
                errors += 1
                continue
            finally:
                field_file.close()

            after_size = compressed.size
            if after_size >= before_size:
                skipped_not_smaller += 1
                continue

            total_before += before_size
            total_after += after_size
            processed += 1

            if not dry_run:
                # field_file.name already includes the upload_to prefix
                # (e.g. "images/xxx.jpg"), but FieldFile.save() re-applies
                # upload_to via generate_filename(), so it must be passed
                # just the basename or the prefix gets doubled.
                new_basename = os.path.basename(as_jpg_name(old_name))
                field_file.storage.delete(old_name)
                field_file.save(new_basename, compressed, save=False)
                instance.save(update_fields=[field_name])

        prefix = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(
            f"{prefix}Processed {processed} images "
            f"({skipped_not_smaller} already smaller than the recompressed "
            f"version, {errors} errors)"
        )
        if processed:
            saved = total_before - total_after
            self.stdout.write(
                f"Total size: {total_before / 1e6:.1f} MB -> {total_after / 1e6:.1f} MB "
                f"(saved {saved / 1e6:.1f} MB, {saved / total_before * 100:.0f}%)"
            )
            self.stdout.write(
                f"Average image size: {total_before / processed / 1e3:.0f} KB -> "
                f"{total_after / processed / 1e3:.0f} KB"
            )
