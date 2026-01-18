from django.urls import path
from . import views

urlpatterns = [
    path('revenue/', views.get_revenue_analytics, name='revenue-analytics'),
    path('users/', views.get_user_analytics, name='user-analytics'),
    path('products/', views.get_product_analytics, name='product-analytics'),
    path('orders/', views.get_order_analytics, name='order-analytics'),
    path('behavior/', views.get_behavior_analytics, name='behavior-analytics'),
    path('top-products/', views.get_top_products, name='top-products'),
    path('top-customers/', views.get_top_customers, name='top-customers'),
]