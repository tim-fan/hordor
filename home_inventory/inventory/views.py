from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Container
from .forms import ItemForm, ContainerForm


@login_required
def index(request):
    item_list = Item.objects.order_by('-creation_date')[:10]
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html', context)


class ItemDetailView(LoginRequiredMixin, generic.DetailView):
    model = Item


class ItemListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 20

    def get_queryset(self):
        return Item.objects.order_by('-creation_date')


class ItemTableView(LoginRequiredMixin, generic.ListView):
    template_name = "inventory/item_table.html"

    def get_queryset(self):
        return Item.objects.order_by('-creation_date')


class ContainerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Container


class ContainerListView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        return Container.objects.order_by('-creation_date')


class ContainerTreeView(LoginRequiredMixin, generic.ListView):
    template_name = 'inventory/tree_view.html'

    def get_queryset(self):
        """
        Queryset is top-level containers - those which are not themselves in a container
        """
        return Container.objects.filter(container__isnull=True)


class NewItemView(LoginRequiredMixin, generic.CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/new_item.html'
    success_url = reverse_lazy('inventory:index')


class NewContainerView(LoginRequiredMixin, generic.CreateView):
    model = Container
    form_class = ContainerForm
    template_name = 'inventory/new_container.html'
    success_url = reverse_lazy('inventory:index')


class ItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Item
    fields = ['name', 'description', 'photo', 'container']
    template_name = 'inventory/item_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:item_detail',
                            kwargs={'pk': self.kwargs['pk']})


class ContainerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Container
    fields = ['name', 'description', 'photo', 'container']
    template_name = 'inventory/container_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:container_detail',
                            kwargs={'pk': self.kwargs['pk']})
