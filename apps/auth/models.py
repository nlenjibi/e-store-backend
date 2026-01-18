"""User and authentication models for the Smart E-Commerce platform."""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class CustomUserManager(BaseUserManager):
    """Custom user manager to handle user creation."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for the e-commerce platform."""
    
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = PhoneNumberField(_('phone number'), blank=True, null=True)
    user_type = models.CharField(_('user type'), max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # For soft deletion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def soft_delete(self):
        """Soft delete the user."""
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=['is_deleted', 'is_active'])


class UserProfile(models.Model):
    """Extended user profile model."""
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('bio'), blank=True)
    gender = models.CharField(_('gender'), max_length=10, choices=GENDER_CHOICES, blank=True)
    location = models.CharField(_('location'), max_length=255, blank=True)
    preferred_language = models.CharField(_('preferred language'), max_length=10, default='en')
    preferred_currency = models.CharField(_('preferred currency'), max_length=3, default='USD')
    newsletter_subscription = models.BooleanField(default=False)
    sms_notification = models.BooleanField(default=True)
    email_notification = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email} Profile"


class Address(models.Model):
    """User address model."""
    
    ADDRESS_TYPE_CHOICES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='home')
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.address_line_1}, {self.city}"

    class Meta:
        ordering = ['-is_default', '-created_at']


class UserActivity(models.Model):
    """Model to track user activities."""
    
    ACTIVITY_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view_product', 'View Product'),
        ('add_to_cart', 'Add to Cart'),
        ('place_order', 'Place Order'),
        ('search', 'Search'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    activity_data = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]