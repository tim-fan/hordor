from django import forms
from .models import Item, Container

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'photo', 'container']

        widgets = {
            'photo': forms.FileInput(attrs={'capture': 'environment'}),
        }

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['name', 'photo', 'container']

        widgets = {
            'photo': forms.FileInput(attrs={'capture': 'environment'}),
        }
    