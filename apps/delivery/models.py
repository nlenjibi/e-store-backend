"""
Delivery Models
---------------
Database models for delivery operations.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class DeliveryAddress(models.Model):
    """
    Customer delivery addresses.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Delivery Addresses"


class BusStation(models.Model):
    """
    Bus stations for pickup (common in African markets).
    """
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class ShippingMethod(models.Model):
    """
    Available shipping methods.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Region(models.Model):
    """
    Delivery regions (e.g., states, provinces).
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Town(models.Model):
    """
    Towns within regions.
    """
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, related_name='towns', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name}, {self.region.name}"
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'region']


class Station(models.Model):
    """
    Delivery/pickup stations within towns.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    town = models.ForeignKey(Town, related_name='stations', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.town.name}"
    
    class Meta:
        ordering = ['name']


class DeliveryFee(models.Model):
    """
    Delivery fees based on town and delivery method.
    """
    DELIVERY_METHODS = [
        ('BUS_STATION', 'Bus Station Pickup'),
        ('HOME_DELIVERY', 'Home Delivery'),
    ]
    
    town = models.ForeignKey(Town, related_name='delivery_fees', on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=DELIVERY_METHODS)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(help_text="Estimated delivery time in days")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.town.name} - {self.get_method_display()}: {self.fee}"
    
    class Meta:
        ordering = ['town', 'method']
        unique_together = ['town', 'method']
