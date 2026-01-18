"""
Reports URLs
------------
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ReportViewSet, basename='report')
router.register('scheduled', views.ScheduledReportViewSet, basename='scheduled-report')
router.register('exports', views.ReportExportViewSet, basename='report-export')

urlpatterns = [
    path('', include(router.urls)),
]
