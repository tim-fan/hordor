from django import forms
from .models import Item, Container


class ItemForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = ['name', 'description']

        widgets = {
            'name':
            forms.TextInput(attrs={'class': 'form-control'}),
            'description':
            forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class ContainerForm(forms.ModelForm):

    container = forms.ModelChoiceField(
        required=False,
        empty_label="None",
        queryset=Container.objects.order_by('-creation_date'))

    class Meta:
        model = Container
        fields = ['name', 'description', 'container']

        widgets = {
            'name':
            forms.TextInput(attrs={'class': 'form-control'}),
            'description':
            forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class ContainerSelectForm(forms.Form):
    """
    Used on the store-item page to let the user override the
    auto-suggested container.
    """
    container = forms.ModelChoiceField(
        queryset=Container.objects.order_by('-creation_date'),
        required=True)
