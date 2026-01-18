"""
Payment Permissions
-------------------
Custom permissions for payment operations.
"""
from rest_framework import permissions


class CanInitiatePayment(permissions.BasePermission):
    """
    Permission to initiate payments.
    
    Users can only initiate payments for their own orders.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only pay for their own orders
        return obj.user == request.user


class CanProcessRefund(permissions.BasePermission):
    """
    Permission to process refunds.
    
    Only staff can process refunds.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CanViewAllPayments(permissions.BasePermission):
    """
    Permission to view all payments.
    
    Only admin users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
