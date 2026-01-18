"""Reviews URL configuration - delegates to products app."""
from django.urls import path
from apps.products.views import (
    ProductReviewListView,
    ProductReviewDetailView
)

urlpatterns = [
    # Reviews are managed within products app
    # These routes redirect to product review endpoints
    path('products/<uuid:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('products/<uuid:product_id>/<uuid:pk>/', ProductReviewDetailView.as_view(), name='product-review-detail'),
]
