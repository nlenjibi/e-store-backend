from django.urls import path
from . import views

urlpatterns = [
    path('coupons/', views.list_active_coupons, name='list-active-coupons'),
    path('flash-sales/', views.list_active_flash_sales, name='list-active-flash-sales'),
    path('banners/', views.list_active_banners, name='list-active-banners'),
    path('all/', views.get_active_promotions, name='get-active-promotions'),
    path('apply-coupon/', views.apply_coupon, name='apply-coupon'),
    path('product/<int:product_id>/flash-sales/', views.get_product_flash_sales, name='get-product-flash-sales'),
    
    # Admin endpoints
    path('admin/coupons/', views.admin_list_coupons, name='admin-list-coupons'),
    path('admin/coupons/create/', views.admin_create_coupon, name='admin-create-coupon'),
    path('admin/flash-sales/', views.admin_list_flash_sales, name='admin-list-flash-sales'),
    path('admin/flash-sales/create/', views.admin_create_flash_sale, name='admin-create-flash-sale'),
    path('admin/banners/', views.admin_list_banners, name='admin-list-banners'),
    path('admin/banners/create/', views.admin_create_banner, name='admin-create-banner'),
]