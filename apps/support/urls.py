"""
Support URLs
------------
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import HelpSupportSettingsView

router = DefaultRouter()
router.register('contact', views.ContactMessageViewSet, basename='contact')
router.register('tickets', views.SupportTicketViewSet, basename='ticket')
router.register('faq', views.FAQViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
    path('settings/', HelpSupportSettingsView.as_view(), name='help-support-settings'),
]
