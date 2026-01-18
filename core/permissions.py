"""
Core Permissions
----------------
Reusable permission classes for the entire project.

Purpose:
- Define common permission patterns
- Enforce access control
- Keep views thin
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    
    Assumes the model has a 'user' field.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access to owner only.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone, write access to admin only.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class IsCustomerOnly(permissions.BasePermission):
    """
    Only allow non-staff users (customers).
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_staff


class IsStaffOrOwner(permissions.BasePermission):
    """
    Allow access to staff or object owner.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        return hasattr(obj, 'user') and obj.user == request.user
