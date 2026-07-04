from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from .imaging import as_jpg_name, compress_image_file


class GenericObject(models.Model):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    description = models.TextField(null=False, blank=True)
    container = models.ForeignKey('Container',
                                  on_delete=models.SET_NULL,
                                  blank=True,
                                  null=True,
                                  related_name='stored_%(class)ss')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Container(GenericObject):
    photo = models.ImageField(upload_to='images/', null=True, blank=True)

    def clean(self):
        super().clean()
        seen = {self.pk} if self.pk is not None else set()
        ancestor = self.container
        while ancestor is not None:
            if ancestor.pk in seen:
                raise ValidationError(
                    "A container cannot be stored inside itself, "
                    "directly or via another container."
                )
            seen.add(ancestor.pk)
            ancestor = ancestor.container

    def save(self, *args, **kwargs):
        if self.photo and not self.photo._committed:
            compressed = compress_image_file(self.photo)
            self.photo.save(as_jpg_name(self.photo.name), compressed, save=False)
        super().save(*args, **kwargs)


class Item(GenericObject):
    main_photo = models.ForeignKey('ItemPhoto',
                                   on_delete=models.SET_NULL,
                                   blank=True,
                                   null=True,
                                   related_name='+')

    def can_be_stored(self):
        """Returns True if item can be stored (not in container and not dispossessed)"""
        if self.container:
            return False
        # Check if item is dispossessed (stored in "Dispossessed" container)
        # For now, just check if container is None
        return True
    
    def can_be_retrieved(self):
        """Returns True if item can be retrieved (is in a container and not dispossessed)"""
        if not self.container:
            return False
        # Check if container is "Dispossessed" 
        if self.container.name and self.container.name.lower() == "dispossessed":
            return False
        return True
    
    def is_dispossessed(self):
        """Returns True if item is in the Dispossessed container"""
        if self.container and self.container.name and self.container.name.lower() == "dispossessed":
            return True
        return False

    def save(self, *args, **kwargs):
        # if moved container, create ItemMovement record
        is_new_item = False
        is_moved_item = False

        if not self.pk:
            # new item - add a movement into the current container
            is_new_item = True
        else:
            # existing item - only add movement if container changed
            original = Item.objects.get(pk=self.pk)
            is_moved_item = original.container != self.container

        # save self before the movement record
        # Prevent exception when item is new
        super().save(*args, **kwargs)
        if is_new_item or is_moved_item:
            ItemMovement.objects.create(
                item=self,
                to_container=self.container,
                is_new_item=is_new_item,
            )
        


class ItemPhoto(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Photo for {self.item.name}"

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image_file(self.image)
            self.image.save(as_jpg_name(self.image.name), compressed, save=False)
        super().save(*args, **kwargs)


@receiver(post_delete, sender=ItemPhoto)
def cleanup_deleted_item_photo(sender, instance, **kwargs):
    instance.image.delete(save=False)

    try:
        item = Item.objects.get(pk=instance.item_id)
    except Item.DoesNotExist:
        return

    # Item.main_photo has on_delete=SET_NULL, so if the deleted photo was
    # the main photo, Django has already nulled it out by this point.
    # Promote a fallback whenever main_photo is unset but photos remain.
    if item.main_photo_id is None:
        replacement = item.photos.order_by('uploaded_at').first()
        if replacement is not None:
            item.main_photo = replacement
            item.save(update_fields=['main_photo'])


class ItemMovement(models.Model):
    """
    For tracking history of item movements between containers
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    to_container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True, blank=True, related_name='moved_to')
    moved_at = models.DateTimeField(default=timezone.now)
    is_new_item = models.BooleanField(default=False)

    def __str__(self):
        if self.is_new_item:
            if not self.to_container:
                return f"New item {self.item.name} created, not stored in container at {self.moved_at}"
            else:
                return f"New item {self.item.name} stored in {self.to_container} at {self.moved_at}"
        else:
            if not self.to_container:
                return f"{self.item.name} removed from container at {self.moved_at}"
            else:
                return f"{self.item.name} moved to {self.to_container} at {self.moved_at}"