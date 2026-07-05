import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_container_id_alter_item_id_and_more'),
    ]

    operations = [
        # Widen item on ItemPhoto (soon renamed to Photo) so a photo can
        # belong to a container instead.
        migrations.AlterField(
            model_name='itemphoto',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='inventory.item'),
        ),
        migrations.AddField(
            model_name='itemphoto',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='inventory.container'),
        ),
        migrations.AddField(
            model_name='container',
            name='main_photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='inventory.itemphoto'),
        ),
        # Rename rather than drop+recreate: this is the existing ItemPhoto
        # table (with all its data) becoming the shared Photo model.
        # Django updates every FK pointing at ItemPhoto (Item.main_photo,
        # the new Container.main_photo, and ItemPhoto/Photo.item) to
        # target the renamed table automatically.
        migrations.RenameModel(old_name='ItemPhoto', new_name='Photo'),
    ]
