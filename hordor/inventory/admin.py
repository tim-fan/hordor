from django.contrib import admin

# Register your models here.
from .models import Item, Container, ItemMovement
admin.site.register(Item)
admin.site.register(Container)
admin.site.register(ItemMovement)
