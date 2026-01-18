from django.urls import path
from . import views

urlpatterns = [
    path('gateways/', views.list_payment_gateways, name='list-payment-gateways'),
    path('transactions/', views.list_transactions, name='list-transactions'),
    path('transactions/<uuid:transaction_id>/', views.get_transaction, name='get-transaction'),
    path('process/', views.process_payment, name='process-payment'),
    path('refund/', views.request_refund, name='request-refund'),
    path('stats/', views.get_payment_stats, name='payment-stats'),
]