"""Categories URL configuration."""
from django.urls import path
from apps.products.views import (
    CategoryListView,
    CategoryDetailView
)
from apps.products import views as product_views

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    # Featured categories could be added here if needed
    # path('featured/', product_views.featured_categories, name='featured-categories'),
]
