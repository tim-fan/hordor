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

    def save(self, *args, **kwargs):
        # if moved container, create ItemMovement record
        add_movement_record = False
        if not self.pk:
            # new item - add a movement into the current container
            add_movement_record = True
        else:
            # existing item - only add movement if container changed
            original = Item.objects.get(pk=self.pk)
            add_movement_record = original.container != self.container

        if add_movement_record:
            ItemMovement.objects.create(
                item=self,
                to_container=self.container
            )
        super().save(*args, **kwargs)


class ItemMovement(models.Model):
    """
    For tracking history of item movements between containers
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    to_container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True, blank=True, related_name='moved_to')
    moved_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item.name} moved to {self.to_container} at {self.moved_at}"