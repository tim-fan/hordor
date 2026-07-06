from django.contrib import admin

# Register your models here.
from .models import Item, Container, ItemMovement, Photo, ShareLink
admin.site.register(Item)
admin.site.register(Container)
admin.site.register(ItemMovement)
admin.site.register(Photo)


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'expires_at')
    readonly_fields = ('token', 'created_at')
