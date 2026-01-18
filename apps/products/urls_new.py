"""URLs for the products app with slug-based routing."""
from django.urls import path
from . import views_new as views

app_name = 'products'

urlpatterns = [
    # ==================== CATEGORY ENDPOINTS ====================
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # ==================== PRODUCT PUBLIC ENDPOINTS ====================
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('category/<slug:category_slug>/', views.ProductsByCategoryView.as_view(), name='products-by-category'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # ==================== SPECIAL PRODUCT SECTIONS ====================
    path('featured/', views.featured_products, name='featured-products'),
    path('recommended/', views.recommended_products, name='recommended-products'),
    path('trending/', views.trending_products, name='trending-products'),
    path('new-arrivals/', views.new_arrivals, name='new-arrivals'),
    
    # ==================== ADMIN PRODUCT CRUD ====================
    path('admin/products/', views.AdminProductCreateView.as_view(), name='admin-product-create'),
    path('admin/products/<slug:slug>/', views.AdminProductUpdateView.as_view(), name='admin-product-update'),
    path('admin/products/<slug:slug>/delete/', views.AdminProductDeleteView.as_view(), name='admin-product-delete'),
    
    # ==================== ADMIN IMAGE MANAGEMENT ====================
    path('admin/products/<slug:product_slug>/images/', views.AdminProductImagesListView.as_view(), name='admin-product-images-list'),
    path('admin/products/<slug:product_slug>/images/add/', views.AdminProductImageAddView.as_view(), name='admin-product-image-add'),
    path('admin/products/<slug:product_slug>/images/<int:index>/', views.AdminProductImageUpdateView.as_view(), name='admin-product-image-update'),
    path('admin/products/<slug:product_slug>/images/<int:index>/delete/', views.AdminProductImageDeleteView.as_view(), name='admin-product-image-delete'),
    
    # ==================== PRODUCT REVIEWS ====================
    path('<slug:product_slug>/reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('<slug:product_slug>/reviews/<uuid:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
]
