from django.db.models import Count, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.http import require_POST
from .imaging import rotate_image_field
from .models import Item, Container, Photo, ItemMovement
from .forms import ItemForm, ContainerForm, ContainerSelectForm
import re


def _update_url_name(owner):
    return 'inventory:item_update' if isinstance(owner, Item) else 'inventory:container_update'


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


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_items = Item.objects.count()
        try:
            dispossessed = Container.objects.get(name__iexact="dispossessed")
            possessed_items = total_items - Item.objects.filter(container=dispossessed).count()
        except Container.DoesNotExist:
            possessed_items = total_items
        stored_items = Item.objects.filter(container__isnull=False).count()

        empty_bag_count = Container.objects.filter(
            name__istartswith="bag"
        ).annotate(
            item_count=Count('stored_items')
        ).filter(item_count=0).count()

        context.update({
            'total_items': total_items,
            'possessed_items': possessed_items,
            'stored_items': stored_items,
            'empty_bag_count': empty_bag_count,
            'recent_movements': ItemMovement.objects.select_related(
                'item', 'item__main_photo', 'to_container'
            ).order_by('-moved_at')[:10],
        })
        return context


class ItemDetailView(LoginRequiredMixin, generic.DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = self.object.itemmovement_set.order_by('-moved_at')
        return context


class ItemListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 20

    def get_queryset(self):
        return Item.objects.order_by('-creation_date')


class ItemTableView(LoginRequiredMixin, generic.ListView):
    template_name = "inventory/item_table.html"

    def get_container_filter(self):
        return self.request.GET.get('container', '')

    def get_queryset(self):
        items = Item.objects.annotate(
            last_moved=Max('itemmovement__moved_at'),
            movement_count=Count('itemmovement'),
        ).order_by('-last_moved')

        container_filter = self.get_container_filter()
        if container_filter == 'none':
            return items.filter(container__isnull=True)
        if container_filter == 'dispossessed':
            try:
                dispossessed = Container.objects.get(name__iexact="dispossessed")
                return items.filter(container=dispossessed)
            except Container.DoesNotExist:
                return items.none()
        if container_filter:
            return items.filter(container_id=container_filter)

        # No filter: default to hiding dispossessed items.
        try:
            dispossessed = Container.objects.get(name__iexact="dispossessed")
            return items.exclude(container=dispossessed)
        except Container.DoesNotExist:
            return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_filter'] = self.get_container_filter()
        context['containers'] = Container.objects.exclude(
            name__iexact="dispossessed"
        ).order_by('-creation_date')
        now = timezone.now()
        for item in context['item_list']:
            age_days = max((now - item.creation_date).days, 1)
            item.activity_rate = item.movement_count / age_days * 30
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

    def get_initial(self):
        initial = super().get_initial()
        name = self.request.GET.get('name')
        if name:
            initial['name'] = name
        return initial

    def get_success_url(self):
        if self.request.POST.get('action') == 'store':
            return reverse_lazy('inventory:store_item', kwargs={'pk': self.object.pk})
        return reverse_lazy('inventory:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        item = self.object
        main_photo = None
        for uploaded_file in self.request.FILES.getlist('photos'):
            photo = Photo.objects.create(item=item, image=uploaded_file)
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

    def form_valid(self, form):
        response = super().form_valid(form)
        container = self.object
        main_photo = None
        for uploaded_file in self.request.FILES.getlist('photos'):
            photo = Photo.objects.create(container=container, image=uploaded_file)
            if main_photo is None:
                main_photo = photo
        if main_photo is not None:
            container.main_photo = main_photo
            container.save(update_fields=['main_photo'])
        return response


class ItemUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:item_detail',
                            kwargs={'pk': self.kwargs['pk']})


@login_required
@require_POST
def delete_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    name = item.name
    item.delete()
    messages.success(request, f'Deleted "{name}".')
    return redirect('inventory:index')


class ContainerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Container
    form_class = ContainerForm
    template_name = 'inventory/container_update.html'

    def get_success_url(self):
        return reverse_lazy('inventory:container_detail',
                            kwargs={'pk': self.kwargs['pk']})


@login_required
def store_item_view(request, pk):
    """
    Store an item. Defaults to the lowest-numbered empty bag; the user
    can override this via the container picker on this page.
    GET: Show instruction page with the suggested (or chosen) container
    POST: Update item's container and redirect to item detail
    """
    item = get_object_or_404(Item, pk=pk)

    if not item.can_be_stored():
        messages.error(request, "This item cannot be stored.")
        return redirect('inventory:item_detail', pk=pk)

    suggested_bag = get_lowest_available_bag()

    if request.method == 'POST':
        form = ContainerSelectForm(request.POST)
        if form.is_valid():
            container = form.cleaned_data['container']
            item.container = container
            item.save()
            messages.success(request, f"Item stored in {container.name}")
            return redirect('inventory:item_detail', pk=pk)
    else:
        initial = {'container': suggested_bag.pk} if suggested_bag else None
        form = ContainerSelectForm(initial=initial)

    context = {
        'item': item,
        'bag': suggested_bag,
        'form': form,
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


def _add_photos(request, owner):
    """
    Add one or more photos to an item or container. If the owner has no
    main photo yet, the first uploaded photo becomes the main photo.
    Shared by add_item_photos_view / add_container_photos_view.
    """
    main_photo = owner.main_photo
    owner_kwargs = {'item': owner} if isinstance(owner, Item) else {'container': owner}

    for uploaded_file in request.FILES.getlist('photos'):
        photo = Photo.objects.create(image=uploaded_file, **owner_kwargs)
        if main_photo is None:
            main_photo = photo

    if main_photo != owner.main_photo:
        owner.main_photo = main_photo
        owner.save(update_fields=['main_photo'])

    return redirect(_update_url_name(owner), pk=owner.pk)


@login_required
@require_POST
def add_item_photos_view(request, pk):
    return _add_photos(request, get_object_or_404(Item, pk=pk))


@login_required
@require_POST
def add_container_photos_view(request, pk):
    return _add_photos(request, get_object_or_404(Container, pk=pk))


@login_required
@require_POST
def set_main_photo_view(request, photo_pk):
    """
    Set an existing photo as its owner's (item or container) main photo.
    """
    photo = get_object_or_404(Photo, pk=photo_pk)
    owner = photo.owner
    owner.main_photo = photo
    owner.save(update_fields=['main_photo'])
    return redirect(_update_url_name(owner), pk=owner.pk)


@login_required
@require_POST
def delete_photo_view(request, photo_pk):
    """
    Delete a photo. If it was the owner's main photo, another remaining
    photo (if any) is promoted to main automatically.
    """
    photo = get_object_or_404(Photo, pk=photo_pk)
    owner = photo.owner
    url_name = _update_url_name(owner)
    owner_pk = owner.pk
    photo.delete()
    return redirect(url_name, pk=owner_pk)


@login_required
@require_POST
def rotate_photo_view(request, photo_pk):
    """
    Rotate a photo 90 degrees clockwise, rewriting the file in place.
    """
    photo = get_object_or_404(Photo, pk=photo_pk)
    owner = photo.owner
    rotate_image_field(photo.image, degrees=-90)
    photo.save(update_fields=['image'])
    return redirect(_update_url_name(owner), pk=owner.pk)
