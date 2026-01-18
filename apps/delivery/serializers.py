"""
Delivery Serializers
--------------------
"""
from rest_framework import serializers
from .models import Region, Town, Station, DeliveryFee


class DeliveryAddressSerializer(serializers.Serializer):
    pass


class BusStationSerializer(serializers.Serializer):
    pass


class ShippingMethodSerializer(serializers.Serializer):
    pass


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for regions."""
    
    class Meta:
        model = Region
        fields = ['id', 'name', 'code']


class TownSerializer(serializers.ModelSerializer):
    """Serializer for towns."""
    region_id = serializers.IntegerField(source='region.id', read_only=True)
    
    class Meta:
        model = Town
        fields = ['id', 'name', 'region_id']


class StationSerializer(serializers.ModelSerializer):
    """Serializer for stations."""
    town_id = serializers.IntegerField(source='town.id', read_only=True)
    
    class Meta:
        model = Station
        fields = ['id', 'name', 'address', 'town_id']


class DeliveryFeeSerializer(serializers.ModelSerializer):
    """Serializer for delivery fees."""
    town_id = serializers.IntegerField(source='town.id', read_only=True)
    
    class Meta:
        model = DeliveryFee
        fields = ['id', 'town_id', 'method', 'fee', 'estimated_days']
