from django.contrib import admin

# Register your models here.
from .models import Item, Container
admin.site.register(Item)
admin.site.register(Container)