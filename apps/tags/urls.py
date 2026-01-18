"""Tags URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    # Tag management
    path('', views.TagListView.as_view(), name='tag-list'),
    path('<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('<slug:tag_slug>/products/', views.products_by_tag, name='products-by-tag'),
    
    # Product-Tag relationships
    path('products/<uuid:product_id>/tags/', views.product_tags, name='product-tags'),
    path('products/<uuid:product_id>/tags/assign/', views.assign_tag_to_product, name='assign-tag'),
    path('products/<uuid:product_id>/tags/<uuid:tag_id>/remove/', views.remove_tag_from_product, name='remove-tag'),
]
