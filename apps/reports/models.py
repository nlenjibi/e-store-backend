"""
Reports Models
--------------
Database models for report generation and scheduling.
"""
from django.db import models
from django.conf import settings


class ScheduledReport(models.Model):
    """
    Scheduled reports for automated generation.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    REPORT_TYPE_CHOICES = [
        ('sales', 'Sales Report'),
        ('revenue', 'Revenue Report'),
        ('inventory', 'Inventory Report'),
        ('customers', 'Customer Report'),
        ('orders', 'Order Report'),
    ]
    
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.JSONField(default=list, help_text="Email addresses to send report")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Scheduled Report"
        verbose_name_plural = "Scheduled Reports"
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class ReportExport(models.Model):
    """
    Track report exports/downloads.
    """
    EXPORT_FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    report_type = models.CharField(max_length=50)
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMAT_CHOICES)
    file_path = models.CharField(max_length=500, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")
    
    class Meta:
        verbose_name = "Report Export"
        verbose_name_plural = "Report Exports"
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_type} - {self.get_export_format_display()} ({self.generated_at})"
