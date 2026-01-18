from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cart, name='get-cart'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('guest/', views.guest_get_cart, name='guest-get-cart'),
    path('guest/add/', views.guest_add_to_cart, name='guest-add-to-cart'),
    path('item/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('item/<int:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
]