from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
import uuid
from .models import PaymentGateway, Transaction, Refund
from .serializers import (
    PaymentGatewaySerializer, TransactionSerializer, RefundSerializer,
    ProcessPaymentSerializer, RefundRequestSerializer
)
from apps.orders.models import Order


@api_view(['GET'])
def list_payment_gateways(request):
    """Get all active payment gateways"""
    gateways = PaymentGateway.objects.filter(is_active=True)
    serializer = PaymentGatewaySerializer(gateways, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_transactions(request):
    """Get all transactions for the authenticated user"""
    transactions = Transaction.objects.filter(user=request.user).select_related('order', 'gateway')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction(request, transaction_id):
    """Get a specific transaction for the authenticated user"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    serializer = TransactionSerializer(transaction)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """Process a payment using a specific gateway"""
    serializer = ProcessPaymentSerializer(data=request.data)
    if serializer.is_valid():
        order_id = serializer.validated_data['order_id']
        gateway_name = serializer.validated_data['gateway_name']
        amount = serializer.validated_data['amount']
        
        # Validate order belongs to user and is valid
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate gateway
        try:
            gateway = PaymentGateway.objects.get(name=gateway_name, is_active=True)
        except PaymentGateway.DoesNotExist:
            return Response({'error': 'Payment gateway not supported'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount matches order total
        if amount != order.total_amount:
            return Response({'error': 'Amount does not match order total'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            order=order,
            user=request.user,
            gateway=gateway,
            reference=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            amount=amount,
            description=f"Payment for order {order.order_number}",
            status='pending'
        )
        
        # Here we would integrate with the actual payment gateway
        # For now, we'll simulate a successful payment
        # In a real implementation, this would involve calling the gateway's API
        try:
            # Simulate payment processing
            # This is where you'd integrate with Stripe, PayPal, etc.
            payment_result = simulate_payment_processing(gateway_name, serializer.validated_data)
            
            if payment_result['success']:
                transaction.status = 'completed'
                transaction.gateway_response = payment_result.get('response', {})
                transaction.completed_at = payment_result.get('completed_at')
                transaction.save()
                
                # Update order payment status
                order.payment_status = 'paid'
                order.save()
                
                return Response({
                    'success': True,
                    'transaction': TransactionSerializer(transaction).data,
                    'message': 'Payment processed successfully'
                })
            else:
                transaction.status = 'failed'
                transaction.gateway_response = payment_result.get('error', {})
                transaction.save()
                
                return Response({
                    'success': False,
                    'error': payment_result.get('message', 'Payment failed'),
                    'transaction': TransactionSerializer(transaction).data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            transaction.status = 'failed'
            transaction.gateway_response = {'error': str(e)}
            transaction.save()
            
            return Response({
                'success': False,
                'error': 'Payment processing error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def simulate_payment_processing(gateway_name, payment_data):
    """
    Simulate payment processing for different gateways
    In a real implementation, this would integrate with actual payment APIs
    """
    # In a real app, this would make actual API calls to payment gateways
    import datetime
    from django.utils import timezone
    
    # Simulate different gateway responses
    if gateway_name == 'stripe':
        # Simulate Stripe processing
        return {
            'success': True,
            'response': {
                'gateway': 'stripe',
                'status': 'succeeded',
                'payment_intent_id': f"pi_{uuid.uuid4().hex[:16]}",
                'client_secret': f"pi_{uuid.uuid4().hex}_secret_{uuid.uuid4().hex[:8]}"
            },
            'completed_at': timezone.now()
        }
    elif gateway_name == 'paypal':
        # Simulate PayPal processing
        return {
            'success': True,
            'response': {
                'gateway': 'paypal',
                'status': 'completed',
                'transaction_id': f"PAY-{uuid.uuid4().hex[:16].upper()}",
                'payer_id': f"PAYER-{uuid.uuid4().hex[:10].upper()}"
            },
            'completed_at': timezone.now()
        }
    elif gateway_name == 'paystack':
        # Simulate Paystack processing
        return {
            'success': True,
            'response': {
                'gateway': 'paystack',
                'status': 'success',
                'reference': f"ref_{uuid.uuid4().hex}",
                'authorization_url': 'https://checkout.paystack.com/mock'
            },
            'completed_at': timezone.now()
        }
    elif gateway_name == 'flutterwave':
        # Simulate Flutterwave processing
        return {
            'success': True,
            'response': {
                'gateway': 'flutterwave',
                'status': 'successful',
                'transaction_id': f"flw_tx_{uuid.uuid4().hex[:12]}",
                'flw_ref': f"flw_{uuid.uuid4().hex[:10]}"
            },
            'completed_at': timezone.now()
        }
    else:
        # Simulate other gateways (mobile money, etc.)
        return {
            'success': True,
            'response': {
                'gateway': gateway_name,
                'status': 'successful',
                'reference': f"REF-{uuid.uuid4().hex[:12].upper()}",
                'message': f'Payment processed via {gateway_name}'
            },
            'completed_at': timezone.now()
        }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund(request):
    """Request a refund for a transaction"""
    serializer = RefundRequestSerializer(data=request.data)
    if serializer.is_valid():
        transaction_id = serializer.validated_data['transaction_id']
        reason = serializer.validated_data['reason']
        amount = serializer.validated_data['amount']
        
        # Validate transaction belongs to user
        try:
            transaction = Transaction.objects.get(
                id=transaction_id, 
                user=request.user,
                status='completed'  # Only completed transactions can be refunded
            )
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found or not eligible for refund'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate refund amount
        if amount > transaction.amount:
            return Response({'error': 'Refund amount exceeds transaction amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create refund record
        refund = Refund.objects.create(
            transaction=transaction,
            order=transaction.order,
            user=request.user,
            reason=reason,
            requested_amount=amount
        )
        
        # In a real implementation, this would process the refund with the payment gateway
        # For now, we'll set it to approved for simulation
        refund.status = 'approved'
        refund.refunded_amount = amount
        refund.processed_at = refund.requested_at
        refund.completed_at = refund.requested_at
        refund.save()
        
        # Update transaction status to refunded if fully refunded
        if amount >= transaction.amount:
            transaction.status = 'refunded'
            transaction.save()
        
        return Response({
            'success': True,
            'refund': RefundSerializer(refund).data,
            'message': 'Refund request processed successfully'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_stats(request):
    """Get payment statistics for the authenticated user"""
    transactions = Transaction.objects.filter(user=request.user)
    
    stats = {
        'total_transactions': transactions.count(),
        'successful_payments': transactions.filter(status='completed').count(),
        'failed_payments': transactions.filter(status='failed').count(),
        'total_paid': sum(t.amount for t in transactions.filter(status='completed')),
        'pending_payments': transactions.filter(status='pending').count(),
    }
    
    return Response(stats)