from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Item, Container

def index(request):
    item_list = Item.objects.order_by('-creation_date')
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html',context)

def item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'inventory/item.html', {'item': item})


def container(request, container_id):
    container = get_object_or_404(Container, pk=container_id)
    return render(request, 'inventory/container.html', {'container': container})