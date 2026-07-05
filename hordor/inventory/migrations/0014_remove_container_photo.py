from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_migrate_container_photo_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='container',
            name='photo',
        ),
    ]
