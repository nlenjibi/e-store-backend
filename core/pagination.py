"""
Core Pagination
---------------
Custom pagination classes for consistent API responses.

Purpose:
- Standardize pagination across all endpoints
- Provide metadata about pagination
- Support different pagination styles
"""
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with customizable page size.
    
    Default: 20 items per page
    Max: 100 items per page
    
    Query params:
    - ?page=2
    - ?page_size=50
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return paginated response with metadata.
        
        Format:
        {
            "count": 100,
            "next": "http://...",
            "previous": "http://...",
            "total_pages": 5,
            "current_page": 2,
            "results": [...]
        }
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets (admin views).
    
    Default: 50 items per page
    Max: 500 items per page
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for small result sets.
    
    Default: 10 items per page
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Alternative pagination using limit/offset.
    
    Query params:
    - ?limit=20
    - ?offset=40
    """
    default_limit = 20
    max_limit = 100
