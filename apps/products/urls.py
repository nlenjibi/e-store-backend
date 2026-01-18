"""URLs for the products app."""
from django.urls import path
from . import views
from . import image_views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('brands/<uuid:pk>/', views.BrandDetailView.as_view(), name='brand-detail'),
    
    # Product endpoints by integer ID (for frontend compatibility)
    path('<int:product_id>/rating/', views.ProductRatingView.as_view(), name='product-rating-by-id'),
    path('<int:product_id>/reviews/', views.ProductReviewsView.as_view(), name='product-reviews-by-id'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Product Reviews by UUID
    path('products/<uuid:product_id>/reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('products/<uuid:product_id>/reviews/<uuid:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    
    # Product Images
    path('products/<uuid:product_id>/images/', image_views.ProductImageListView.as_view(), name='product-image-list'),
    path('products/<uuid:product_id>/images/<uuid:image_id>/', image_views.ProductImageDetailView.as_view(), name='product-image-detail'),
    path('products/<uuid:product_id>/images/<uuid:image_id>/set-primary/', image_views.set_primary_image, name='set-primary-image'),
    path('products/<uuid:product_id>/images/reorder/', image_views.reorder_images, name='reorder-images'),
    path('products/<uuid:product_id>/images/bulk-upload/', image_views.bulk_upload_images, name='bulk-upload-images'),
    
    # Product Collections
    path('featured/', views.featured_products, name='featured-products'),
    path('trending/', views.trending_products, name='trending-products'),
    path('recently-viewed/', views.recently_viewed_products, name='recently-viewed-products'),
    path('top-rated/', views.top_rated_products, name='top-rated-products'),
    path('frequently-purchased/', views.frequently_purchased_products, name='frequently-purchased-products'),
]