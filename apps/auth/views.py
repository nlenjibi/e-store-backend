"""Views for the accounts app."""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import User, UserProfile, Address, UserActivity
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserSerializer, UserProfileSerializer, AddressSerializer, 
    UserActivitySerializer
)
from .permissions import IsOwnerOrAdmin


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        # Create user profile
        UserProfile.objects.get_or_create(user=user)
        
        # Send verification email
        self.send_verification_email(user)
    
    def send_verification_email(self, user):
        """Send email verification to the user."""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_link = f"{settings.FRONTEND_URL}/verify/{uid}/{token}/"
        
        subject = 'Verify your email address'
        message = render_to_string('accounts/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserLoginView(generics.GenericAPIView):
    """View for user login."""
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        login(request, user)
        
        refresh = RefreshToken.for_user(user)
        
        # Update last login time
        user.last_login_at = user.last_login
        user.save(update_fields=['last_login_at'])
        
        # Log user activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """View for user logout."""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        
        # Log user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class AddressListView(generics.ListCreateAPIView):
    """View for listing and creating addresses."""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)
    
    def perform_create(self, serializer):
        # If this is the first address, make it default
        if not Address.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user, is_default=True)
        else:
            serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting an address."""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class UserActivityView(generics.ListAPIView):
    """View for user activities."""
    
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)