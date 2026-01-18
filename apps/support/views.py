"""
Support Views
-------------
"""
from rest_framework import viewsets


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    Handle contact form submissions.
    """
    pass


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for support tickets.
    """
    pass


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List FAQs.
    """
    pass
