from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render
from .models import Item, Container
from .forms import ItemForm, ContainerForm


def index(request):
    item_list = Item.objects.order_by('-creation_date')
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html', context)


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


class ContainerTreeView(generic.ListView):
    template_name = 'inventory/tree_view.html'

    def get_queryset(self):
        """
        Queryset is top-level containers - those which are not themselves in a container
        """
        return Container.objects.filter(container__isnull=True)


class NewItemView(generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/new_item.html'
    success_url = reverse_lazy('inventory:index')


class NewContainerView(generic.CreateView):
    model = Container
    form_class = ContainerForm
    template_name = 'inventory/new_container.html'
    success_url = reverse_lazy('inventory:index')


class ItemUpdateView(generic.UpdateView):
    model = Item
    fields = ['name', 'photo', 'container']
    template_name = 'inventory/item_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:item_detail',
                            kwargs={'pk': self.kwargs['pk']})


class ContainerUpdateView(generic.UpdateView):
    model = Container
    fields = ['name', 'photo', 'container']
    template_name = 'inventory/container_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:container_detail',
                            kwargs={'pk': self.kwargs['pk']})
