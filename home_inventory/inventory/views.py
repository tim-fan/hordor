from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render
from .models import Item, Container
from .forms import ItemForm

def index(request):
    item_list = Item.objects.order_by('-creation_date')
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html',context)

class ItemDetailView(generic.DetailView):
    model = Item

class ItemListView(generic.ListView):
    def get_queryset(self):
        return Item.objects.order_by('-creation_date')

class ContainerDetailView(generic.DetailView):
    model = Container

class ContainerListView(generic.ListView):
    def get_queryset(self):
        return Container.objects.order_by('-creation_date')

class NewItemView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/new_item.html'
    success_url = reverse_lazy('inventory:index')