from django.db import migrations


def copy_item_photo_to_itemphoto(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')
    ItemPhoto = apps.get_model('inventory', 'ItemPhoto')

    for item in Item.objects.exclude(photo='').exclude(photo__isnull=True):
        photo = ItemPhoto.objects.create(item=item, image=item.photo.name)
        item.main_photo = photo
        item.save(update_fields=['main_photo'])


def noop_reverse(apps, schema_editor):
    # Data is still readable from the old `photo` field until the next
    # migration removes it, so there's nothing to restore on reverse.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_item_photos'),
    ]

    operations = [
        migrations.RunPython(copy_item_photo_to_itemphoto, noop_reverse),
    ]
