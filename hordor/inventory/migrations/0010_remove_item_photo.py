from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_migrate_item_photo_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='photo',
        ),
    ]
