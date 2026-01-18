"""Utility functions for the products app."""
from .models import ProductView, ProductSearch


def track_product_view(product, user=None, session_key=None, ip_address=None, user_agent=None):
    """Track a product view."""
    ProductView.objects.create(
        product=product,
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent
    )


def track_search(query, user=None, session_key=None, ip_address=None, results_count=0):
    """Track a product search."""
    ProductSearch.objects.create(
        query=query,
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        results_count=results_count
    )