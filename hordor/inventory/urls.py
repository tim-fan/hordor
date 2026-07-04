from django.urls import path

from . import views

app_name = "inventory"
urlpatterns = [
    path('', views.ItemTableView.as_view(), name="index"),
    path('store/', views.quick_store_view, name='quick_store'),
    path('retrieve/', views.quick_retrieve_view, name='quick_retrieve'),
    path('<int:pk>/item', views.ItemDetailView.as_view(), name='item_detail'),
    path('<int:pk>/item/update',
         views.ItemUpdateView.as_view(),
         name='item_update'),
    path('<int:pk>/item/store', views.store_item_view, name='store_item'),
    path('<int:pk>/item/retrieve', views.retrieve_item_view, name='retrieve_item'),
    path('<int:pk>/item/photos/add', views.add_item_photos_view, name='add_item_photos'),
    path('photo/<int:photo_pk>/set_main', views.set_main_item_photo_view, name='set_main_item_photo'),
    path('photo/<int:photo_pk>/delete', views.delete_item_photo_view, name='delete_item_photo'),
    path('item/list/', views.ItemListView.as_view(), name='item_list'),
    path('item/table/', views.ItemTableView.as_view(), name='item_table'),
    path('item/new/', views.NewItemView.as_view(), name='new_item'),
    path('item/new/store/', views.NewItemView.as_view(redirect_to_store=True), name='new_item_to_store'),
    path('<int:pk>/container',
         views.ContainerDetailView.as_view(),
         name='container_detail'),
    path('container/list/',
         views.ContainerListView.as_view(),
         name='container_list'),
    path('container/tree/',
         views.ContainerTreeView.as_view(),
         name='container_tree'),
    path('container/new/',
         views.NewContainerView.as_view(),
         name='new_container'),
    path('<int:pk>/container/update',
         views.ContainerUpdateView.as_view(),
         name='container_update'),
]