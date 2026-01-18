"""Serializers for the accounts app."""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Address, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 
                  'phone_number', 'date_of_birth', 'user_type')
        read_only_fields = ('id', 'user_type')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            if user.is_deleted:
                raise serializers.ValidationError('User account has been deleted')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email and password are required')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model."""
    
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'phone_number', 
                  'date_of_birth', 'avatar', 'is_verified', 'profile', 'created_at', 'updated_at')
        read_only_fields = ('id', 'email', 'is_verified', 'created_at', 'updated_at')


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for address model."""
    
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity model."""
    
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ('id', 'user', 'ip_address', 'user_agent', 'timestamp')