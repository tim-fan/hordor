from django.urls import path

from . import views

app_name="inventory"
urlpatterns = [
    path('', views.index, name="index"),
    path('item/<int:item_id>/', views.item, name='item'),
    path('container/<int:container_id>/', views.container, name='container'),
]