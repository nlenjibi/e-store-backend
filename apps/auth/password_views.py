"""Additional authentication views for password management."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send password reset email."""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'success': False, 'message': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        # Don't reveal if email exists for security
        return Response({
            'success': True,
            'message': 'If that email exists, a password reset link has been sent'
        })
    
    # Generate token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create reset link
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
    
    # Send email
    subject = 'Reset Your Password'
    message = render_to_string('auth/password_reset_email.html', {
        'user': user,
        'reset_link': reset_link,
    })
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        return Response(
            {'success': False, 'message': 'Failed to send email'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'success': True,
        'message': 'Password reset email sent'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token."""
    token = request.data.get('token')
    uid = request.data.get('uid')
    password = request.data.get('password')
    
    if not all([token, uid, password]):
        return Response(
            {'success': False, 'message': 'token, uid, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate password strength
    if len(password) < 8:
        return Response(
            {'success': False, 'message': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'success': False, 'message': 'Invalid reset link'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token
    if not default_token_generator.check_token(user, token):
        return Response(
            {'success': False, 'message': 'Invalid or expired token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Password reset successfully'
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change authenticated user's password."""
    current_password = request.data.get('current_password') or request.data.get('currentPassword')
    new_password = request.data.get('new_password') or request.data.get('newPassword')
    
    if not all([current_password, new_password]):
        return Response(
            {'success': False, 'message': 'current_password and new_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    
    # Verify current password
    if not user.check_password(current_password):
        return Response(
            {'success': False, 'message': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password strength
    if len(new_password) < 8:
        return Response(
            {'success': False, 'message': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh JWT access token."""
    refresh_token = request.data.get('refresh') or request.data.get('refreshToken')
    
    if not refresh_token:
        return Response(
            {'success': False, 'message': 'refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        # Optionally rotate refresh token
        new_refresh_token = str(refresh)
        
        return Response({
            'success': True,
            'access': access_token,
            'accessToken': access_token,
            'refresh': new_refresh_token,
            'refreshToken': new_refresh_token,
            'expiresIn': 900  # 15 minutes in seconds
        })
    except Exception as e:
        return Response(
            {'success': False, 'message': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify user email address."""
    token = request.data.get('token')
    uid = request.data.get('uid')
    
    if not all([token, uid]):
        return Response(
            {'success': False, 'message': 'token and uid are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'success': False, 'message': 'Invalid verification link'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token
    if not default_token_generator.check_token(user, token):
        return Response(
            {'success': False, 'message': 'Invalid or expired token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark email as verified
    user.is_email_verified = True
    user.is_active = True
    user.save()
    
    return Response({
        'success': True,
        'message': 'Email verified successfully'
    })
