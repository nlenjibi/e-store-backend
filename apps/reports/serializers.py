"""
Reports Serializers
-------------------
"""
from rest_framework import serializers
from .models import ScheduledReport, ReportExport


class ScheduledReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledReport
        fields = [
            'id', 'name', 'report_type', 'frequency', 
            'recipients', 'is_active', 'created_at', 'last_run'
        ]
        read_only_fields = ['created_at', 'last_run']


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = [
            'id', 'report_type', 'export_format', 
            'file_path', 'generated_at', 'file_size'
        ]
        read_only_fields = ['generated_at', 'file_size']


class SalesReportSerializer(serializers.Serializer):
    """Serializer for sales report data."""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)


class RevenueReportSerializer(serializers.Serializer):
    """Serializer for revenue report data."""
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method_breakdown = serializers.DictField()
    currency_breakdown = serializers.DictField()


class InventoryReportSerializer(serializers.Serializer):
    """Serializer for inventory report data."""
    total_products = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=10, decimal_places=2)
