"""Custom permissions for the accounts app."""
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to allow owners or admin users."""
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is admin
        if request.user.is_staff:
            return True
        
        # Check if the object has a user attribute and it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For direct user objects
        if isinstance(obj, request.user.__class__):
            return obj == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to allow admin users to edit, others read-only."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsCustomer(permissions.BasePermission):
    """Permission to allow only customer users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'customer'


class IsAdmin(permissions.BasePermission):
    """Permission to allow only admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'admin'