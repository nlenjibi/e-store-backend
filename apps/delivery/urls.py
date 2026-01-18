"""
Delivery URLs
-------------
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('addresses', views.DeliveryAddressViewSet, basename='delivery-address')
router.register('bus-stations', views.BusStationViewSet, basename='bus-station')
router.register('shipping-methods', views.ShippingMethodViewSet, basename='shipping-method')
router.register('regions', views.RegionViewSet, basename='region')
router.register('towns', views.TownViewSet, basename='town')
router.register('fees', views.DeliveryFeeViewSet, basename='delivery-fee')

urlpatterns = [
    path('', include(router.urls)),
]
