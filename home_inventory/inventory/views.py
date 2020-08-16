from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from .models import Item, Container

def index(request):
    item_list = Item.objects.order_by('-creation_date')
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html',context)

def new_item(request):
    return render(request, 'inventory/new_item.html')

def process_new_item(request):
    name = request.POST['name']
    new_item = Item(name=name)
    new_item.save()
    return HttpResponseRedirect(reverse('inventory:index'))

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