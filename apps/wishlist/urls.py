"""Wishlist URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.WishlistListView.as_view(), name='wishlist-list'),
    path('count/', views.wishlist_count, name='wishlist-count'),
    path('toggle/', views.toggle_wishlist, name='wishlist-toggle'),
    path('apply-to-cart/', views.apply_wishlist_to_cart, name='wishlist-apply-to-cart'),
    path('<uuid:product_id>/', views.WishlistDetailView.as_view(), name='wishlist-detail'),
]
