"""Custom permissions for the products app."""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to allow admin users to edit, others read-only."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff