"""
Delivery Views
--------------
API views for delivery operations.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Region, Town, Station, DeliveryFee
from .serializers import (
    RegionSerializer, TownSerializer, StationSerializer, DeliveryFeeSerializer
)


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for delivery addresses.
    """
    pass


class BusStationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List available bus stations for pickup.
    """
    pass


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List available shipping methods.
    """
    pass


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all available regions.
    """
    queryset = Region.objects.filter(is_active=True)
    serializer_class = RegionSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'regions': serializer.data
        })
    
    @action(detail=True, methods=['get'], url_path='towns')
    def towns(self, request, pk=None):
        """Get all towns for a specific region."""
        region = self.get_object()
        towns = Town.objects.filter(region=region, is_active=True)
        serializer = TownSerializer(towns, many=True)
        return Response({
            'success': True,
            'towns': serializer.data
        })


class TownViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for towns.
    """
    queryset = Town.objects.filter(is_active=True)
    serializer_class = TownSerializer
    
    @action(detail=True, methods=['get'], url_path='stations')
    def stations(self, request, pk=None):
        """Get all stations for a specific town."""
        town = self.get_object()
        stations = Station.objects.filter(town=town, is_active=True)
        serializer = StationSerializer(stations, many=True)
        return Response({
            'success': True,
            'stations': serializer.data
        })


class DeliveryFeeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for delivery fees.
    """
    queryset = DeliveryFee.objects.filter(is_active=True)
    serializer_class = DeliveryFeeSerializer
    
    def list(self, request, *args, **kwargs):
        """Get delivery fees filtered by town and method."""
        town_id = request.query_params.get('townId')
        method = request.query_params.get('method')
        
        if not town_id:
            return Response({
                'success': False,
                'error': 'townId parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(town_id=town_id)
        
        if method:
            queryset = queryset.filter(method=method)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'fees': serializer.data
        })
