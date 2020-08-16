from django.urls import path

from . import views

app_name="inventory"
urlpatterns = [
    path('', views.index, name="index"),
    path('item/<int:item_id>/', views.item, name='item'),
    path('item/new/', views.new_item, name='new_item'),
    path('item/process_new/', views.process_new_item, name='process_new_item'),
    path('container/<int:container_id>/', views.container, name='container'),
]