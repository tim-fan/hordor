from django.db import models
from django.utils import timezone


class GenericObject(models.Model):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
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
    pass


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