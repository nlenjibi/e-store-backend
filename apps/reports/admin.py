"""
Reports Admin
-------------
"""
from django.contrib import admin
from .models import ScheduledReport, ReportExport


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'frequency', 'is_active', 'last_run']
    list_filter = ['report_type', 'frequency', 'is_active']
    search_fields = ['name']


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'export_format', 'generated_by', 'generated_at', 'file_size']
    list_filter = ['report_type', 'export_format', 'generated_at']
    search_fields = ['report_type']
