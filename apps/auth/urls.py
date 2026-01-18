"""URLs for the auth app."""
from django.urls import path
from . import views
from . import password_views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    path('refresh/', password_views.refresh_token, name='token-refresh'),
    
    # Password Management
    path('forgot-password/', password_views.forgot_password, name='forgot-password'),
    path('reset-password/', password_views.reset_password, name='reset-password'),
    path('change-password/', password_views.change_password, name='change-password'),
    
    # Email Verification
    path('verify-email/', password_views.verify_email, name='verify-email'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # User Addresses
    path('addresses/', views.AddressListView.as_view(), name='address-list'),
    path('addresses/<uuid:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    
    # User Activity
    path('activities/', views.UserActivityView.as_view(), name='user-activities'),
]