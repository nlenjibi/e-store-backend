from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_orders, name='list-orders'),
    path('create/', views.create_order, name='create-order'),
    path('<int:order_id>/', views.get_order, name='get-order'),
    path('<int:order_id>/update/', views.update_order, name='update-order'),
    path('stats/', views.order_stats, name='order-stats'),
]