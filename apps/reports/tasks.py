"""
Reports Tasks
-------------
Celery tasks for scheduled report generation.
"""
from celery import shared_task


@shared_task
def generate_scheduled_reports():
    """
    Generate all active scheduled reports.
    
    Run this task daily via Celery Beat.
    """
    pass


@shared_task
def generate_sales_report(start_date, end_date, recipients):
    """
    Generate and email sales report.
    """
    pass


@shared_task
def generate_revenue_report(period, recipients):
    """
    Generate and email revenue report.
    """
    pass


@shared_task
def cleanup_old_exports(days=30):
    """
    Delete report exports older than specified days.
    """
    pass
