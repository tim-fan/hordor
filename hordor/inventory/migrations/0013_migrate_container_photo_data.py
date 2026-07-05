from django.db import migrations


def copy_container_photo_to_photo(apps, schema_editor):
    Container = apps.get_model('inventory', 'Container')
    Photo = apps.get_model('inventory', 'Photo')

    for container in Container.objects.exclude(photo='').exclude(photo__isnull=True):
        photo = Photo.objects.create(container=container, image=container.photo.name)
        container.main_photo = photo
        container.save(update_fields=['main_photo'])


def noop_reverse(apps, schema_editor):
    # Data is still readable from the old `photo` field until the next
    # migration removes it, so there's nothing to restore on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_photo_shared_model'),
    ]

    operations = [
        migrations.RunPython(copy_container_photo_to_photo, noop_reverse),
    ]
