from django.contrib import admin

# Register your models here.
from .models import Item, Container, ItemMovement, Photo
admin.site.register(Item)
admin.site.register(Container)
admin.site.register(ItemMovement)
admin.site.register(Photo)
