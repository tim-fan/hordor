from django import forms
from .models import Item
from camera_imagefield import CameraImageWidget


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'photo', 'container']
        widgets = {
            'photo': CameraImageWidget(),
        }