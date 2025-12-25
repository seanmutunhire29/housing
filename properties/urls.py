from django.urls import path
from .views import (PropertyListView, PropertyDetailView, create_property,
                   update_property, delete_property, toggle_favorite,
                   my_properties, my_favorites)

urlpatterns = [
    path('', PropertyListView.as_view(), name='property_list'),
    path('<uuid:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('create/', create_property, name='property_create'),
    path('<uuid:pk>/update/', update_property, name='property_update'),
    path('<uuid:pk>/delete/', delete_property, name='property_delete'),
    path('<uuid:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('my-properties/', my_properties, name='my_properties'),
    path('favorites/', my_favorites, name='my_favorites'),
]