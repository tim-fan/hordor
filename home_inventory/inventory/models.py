from django.db import models
from django.utils import timezone

class GenericObject(models.Model):
    name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created', default=timezone.now)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    container = models.ForeignKey('Container', on_delete=models.SET_NULL, blank=True, null=True, related_name='stored_%(class)ss')
    
    def __str__(self):
        return self.name
    class Meta:
        abstract = True
    
class Container(GenericObject):
    pass

class Item(GenericObject):
    pass
