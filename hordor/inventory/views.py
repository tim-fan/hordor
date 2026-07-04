from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Item, Container, ItemPhoto
from .forms import ItemForm, ContainerForm
import re


def items_by_recent_movement():
    """
    All items, most recently stored/retrieved/created first.
    """
    return Item.objects.annotate(
        last_moved=Max('itemmovement__moved_at')
    ).order_by('-last_moved')


def get_lowest_available_bag():
    """
    Find the lowest-numbered bag that doesn't contain any items.
    Returns the Container object, or None if no bags are available.
    """
    # Get all containers that start with "Bag"
    bags = Container.objects.filter(name__istartswith="bag")
    
    # Build list of (bag_number, bag_object) tuples for bags that are empty
    available_bags = []
    
    for bag in bags:
        # Extract number from bag name (e.g., "Bag 42" -> 42)
        match = re.search(r'\d+', bag.name)
        if match:
            bag_number = int(match.group())
            # Check if bag is empty (no items stored in it)
            if not bag.stored_items.exists():
                available_bags.append((bag_number, bag))
    
    # Sort by bag number and return the lowest one
    if available_bags:
        available_bags.sort(key=lambda x: x[0])
        return available_bags[0][1]  # Return the bag object
    
    return None


@login_required
def index(request):
    item_list = Item.objects.order_by('-creation_date')[:10]
    container_list = Container.objects.order_by('-creation_date')
    context = {
        'item_list': item_list,
        'container_list': container_list,
    }
    return render(request, 'inventory/index.html', context)


@login_required
def quick_store_view(request):
    """
    Fast picker for storing an item: shows all storable items, most
    recently moved first, with live name filtering. Tap to jump
    straight to that item's store-confirmation page.
    """
    items = [item for item in items_by_recent_movement() if item.can_be_stored()]
    return render(request, 'inventory/quick_store.html', {'item_list': items})


@login_required
def quick_retrieve_view(request):
    """
    Fast picker for retrieving an item: shows all retrievable items,
    most recently moved first, with live name filtering. Tap to jump
    straight to that item's retrieve-confirmation page.
    """
    items = [item for item in items_by_recent_movement() if item.can_be_retrieved()]
    return render(request, 'inventory/quick_retrieve.html', {'item_list': items})


class ItemDetailView(LoginRequiredMixin, generic.DetailView):
    model = Item


class ItemListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 20

    def get_queryset(self):
        return Item.objects.order_by('-creation_date')


class ItemTableView(LoginRequiredMixin, generic.ListView):
    template_name = "inventory/item_table.html"

    def show_dispossessed(self):
        return self.request.GET.get('show_dispossessed') == '1'

    def get_queryset(self):
        items = Item.objects.order_by('-creation_date')
        if self.show_dispossessed():
            return items
        try:
            dispossessed = Container.objects.get(name__iexact="dispossessed")
            return items.exclude(container=dispossessed)
        except Container.DoesNotExist:
            return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_dispossessed'] = self.show_dispossessed()
        return context


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
    redirect_to_store = False

    def get_success_url(self):
        if self.redirect_to_store:
            return reverse_lazy('inventory:store_item', kwargs={'pk': self.object.pk})
        return reverse_lazy('inventory:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['redirect_to_store'] = self.redirect_to_store
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        item = self.object
        main_photo = None
        for uploaded_file in self.request.FILES.getlist('photos'):
            photo = ItemPhoto.objects.create(item=item, image=uploaded_file)
            if main_photo is None:
                main_photo = photo
        if main_photo is not None:
            item.main_photo = main_photo
            item.save(update_fields=['main_photo'])
        return response


class NewContainerView(LoginRequiredMixin, generic.CreateView):
    model = Container
    form_class = ContainerForm
    template_name = 'inventory/new_container.html'
    success_url = reverse_lazy('inventory:index')


class ItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Item
    fields = ['name', 'description', 'container']
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


@login_required
def store_item_view(request, pk):
    """
    Store an item in a bag.
    GET: Show instruction page with selected bag
    POST: Update item's container and redirect to item detail
    """
    item = get_object_or_404(Item, pk=pk)
    
    # Check if item can be stored
    if not item.can_be_stored():
        messages.error(request, "This item cannot be stored.")
        return redirect('inventory:item_detail', pk=pk)
    
    # Find the lowest available bag
    bag = get_lowest_available_bag()
    if not bag:
        messages.error(request, "No bags available for storage.")
        return redirect('inventory:item_detail', pk=pk)
    
    if request.method == 'POST':
        # User confirmed they've stored the item
        item.container = bag
        item.save()
        messages.success(request, f"Item stored in {bag.name}")
        return redirect('inventory:item_detail', pk=pk)
    
    # GET request - show instruction page
    context = {
        'item': item,
        'bag': bag,
    }
    return render(request, 'inventory/store_item.html', context)


@login_required
def retrieve_item_view(request, pk):
    """
    Retrieve an item from its container.
    GET: Show instruction page
    POST: Clear item's container and redirect to item detail
    """
    item = get_object_or_404(Item, pk=pk)
    
    # Check if item can be retrieved
    if not item.can_be_retrieved():
        messages.error(request, "This item cannot be retrieved.")
        return redirect('inventory:item_detail', pk=pk)
    
    current_container = item.container
    
    if request.method == 'POST':
        # User confirmed they've retrieved the item
        item.container = None
        item.save()
        messages.success(request, f"Item retrieved from {current_container.name}")
        return redirect('inventory:item_detail', pk=pk)
    
    # GET request - show instruction page
    context = {
        'item': item,
        'container': current_container,
    }
    return render(request, 'inventory/retrieve_item.html', context)


@login_required
@require_POST
def add_item_photos_view(request, pk):
    """
    Add one or more photos to an item. If the item has no main photo yet,
    the first uploaded photo becomes the main photo.
    """
    item = get_object_or_404(Item, pk=pk)
    main_photo = item.main_photo

    for uploaded_file in request.FILES.getlist('photos'):
        photo = ItemPhoto.objects.create(item=item, image=uploaded_file)
        if main_photo is None:
            main_photo = photo

    if main_photo != item.main_photo:
        item.main_photo = main_photo
        item.save(update_fields=['main_photo'])

    return redirect('inventory:item_update', pk=pk)


@login_required
@require_POST
def set_main_item_photo_view(request, photo_pk):
    """
    Set an existing photo as the item's main photo.
    """
    photo = get_object_or_404(ItemPhoto, pk=photo_pk)
    item = photo.item
    item.main_photo = photo
    item.save(update_fields=['main_photo'])
    return redirect('inventory:item_update', pk=item.pk)


@login_required
@require_POST
def delete_item_photo_view(request, photo_pk):
    """
    Delete a photo from an item. If it was the main photo, another
    remaining photo (if any) is promoted to main automatically.
    """
    photo = get_object_or_404(ItemPhoto, pk=photo_pk)
    item_pk = photo.item_id
    photo.delete()
    return redirect('inventory:item_update', pk=item_pk)
