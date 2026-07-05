import secrets

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
    main_photo = models.ForeignKey('Photo',
                                   on_delete=models.SET_NULL,
                                   blank=True,
                                   null=True,
                                   related_name='+')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Container(GenericObject):

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


class Item(GenericObject):

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
        


class Photo(models.Model):
    """
    A photo belonging to exactly one of Item or Container. Shared model
    (rather than one per owner type) so add/rotate/delete/set-main can
    be implemented once and used identically for items and containers.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    container = models.ForeignKey(Container, on_delete=models.CASCADE, null=True, blank=True, related_name='photos')
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    @property
    def owner(self):
        return self.item or self.container

    def __str__(self):
        return f"Photo for {self.owner.name}"

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image_file(self.image)
            self.image.save(as_jpg_name(self.image.name), compressed, save=False)
        super().save(*args, **kwargs)


@receiver(post_delete, sender=Photo)
def cleanup_deleted_photo(sender, instance, **kwargs):
    instance.image.delete(save=False)

    if instance.item_id is not None:
        owner_model, owner_id = Item, instance.item_id
    elif instance.container_id is not None:
        owner_model, owner_id = Container, instance.container_id
    else:
        return

    try:
        owner = owner_model.objects.get(pk=owner_id)
    except owner_model.DoesNotExist:
        return

    # main_photo has on_delete=SET_NULL, so if the deleted photo was the
    # main photo, Django has already nulled it out by this point.
    # Promote a fallback whenever main_photo is unset but photos remain.
    if owner.main_photo_id is None:
        replacement = owner.photos.order_by('uploaded_at').first()
        if replacement is not None:
            owner.main_photo = replacement
            owner.save(update_fields=['main_photo'])


def _generate_share_token():
    return secrets.token_urlsafe(24)


class ShareLink(models.Model):
    """
    A shareable, time-limited, read-only link. Visiting /share/<token>/
    logs the browser in as the dedicated read-only viewer account;
    deleting a ShareLink row revokes it immediately (checked on every
    request by ReadOnlyShareMiddleware), independent of session lifetime.
    """
    token = models.CharField(max_length=64, unique=True, default=_generate_share_token)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"Share link created {self.created_at:%Y-%m-%d}, expires {self.expires_at:%Y-%m-%d}"


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