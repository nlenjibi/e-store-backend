"""Views for the products app with slug-based routing and image management."""
from rest_framework import generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, F
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from .models import Category, Brand, Product, ProductReview
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, 
    ProductListSerializer, ProductCreateUpdateSerializer,
    ProductImageManagementSerializer, ProductReviewSerializer
)
from .permissions import IsAdminOrReadOnly
from core.permissions import IsAdminUser


# ==================== CATEGORY VIEWS ====================

class CategoryListView(generics.ListCreateAPIView):
    """
    List all active categories or create a new category.
    GET /api/products/categories/
    POST /api/products/categories/ (Admin only)
    """
    queryset = Category.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a category by slug.
    GET /api/products/categories/{category_slug}/
    PATCH /api/products/categories/{category_slug}/ (Admin only)
    DELETE /api/products/categories/{category_slug}/ (Admin only)
    """
    queryset = Category.objects.filter(is_active=True, is_deleted=False)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# ==================== PRODUCT LIST & SEARCH VIEWS ====================

class ProductListView(generics.ListAPIView):
    """
    List all active products with filtering and search.
    GET /api/products/
    
    Query Parameters:
    - search: Search in product name, description, SKU
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - in_stock: Filter by stock availability (true/false)
    - shipping_type: Filter by shipping type (STORE/SHIP)
    - category: Filter by category slug
    - is_featured: Filter featured products
    - is_trending: Filter trending products
    - ordering: Sort by price, created_at, rating, discount_percent
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku', 'barcode']
    ordering_fields = ['price', 'created_at', 'rating', 'discount_percent']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, is_deleted=False)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Stock filter
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        # Shipping type filter
        shipping_type = self.request.query_params.get('shipping_type')
        if shipping_type and shipping_type in ['STORE', 'SHIP']:
            queryset = queryset.filter(shipping_type=shipping_type)
        
        # Category filter (by slug)
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Feature filters
        is_featured = self.request.query_params.get('is_featured')
        if is_featured and is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        is_trending = self.request.query_params.get('is_trending')
        if is_trending and is_trending.lower() == 'true':
            queryset = queryset.filter(is_trending=True)
        
        return queryset.select_related('category', 'brand').prefetch_related('reviews')


class ProductDetailView(generics.RetrieveAPIView):
    """
    Retrieve a product by slug.
    GET /api/products/{product_slug}/
    """
    queryset = Product.objects.filter(is_active=True, is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductsByCategoryView(generics.ListAPIView):
    """
    List all products in a specific category by category slug.
    GET /api/products/category/{category_slug}/
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return Product.objects.filter(
            category__slug=category_slug,
            is_active=True,
            is_deleted=False
        ).select_related('category', 'brand')


class ProductSearchView(generics.ListAPIView):
    """
    Search products by name or description.
    GET /api/products/search/?q=iphone
    """
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Product.objects.none()
        
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query),
            is_active=True,
            is_deleted=False
        ).select_related('category', 'brand')


# ==================== SPECIAL PRODUCT SECTIONS ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products(request):
    """
    List featured products.
    GET /api/products/featured/
    """
    products = Product.objects.filter(
        is_featured=True,
        is_active=True,
        is_deleted=False
    ).select_related('category', 'brand')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recommended_products(request):
    """
    List recommended products based on rating.
    GET /api/products/recommended/
    """
    products = Product.objects.filter(
        is_active=True,
        is_deleted=False,
        rating__gte=4.0
    ).select_related('category', 'brand').order_by('-rating', '-num_reviews')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_products(request):
    """
    List trending products.
    GET /api/products/trending/
    """
    products = Product.objects.filter(
        is_trending=True,
        is_active=True,
        is_deleted=False
    ).select_related('category', 'brand')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def new_arrivals(request):
    """
    List new arrival products.
    GET /api/products/new-arrivals/
    """
    products = Product.objects.filter(
        is_new=True,
        is_active=True,
        is_deleted=False
    ).select_related('category', 'brand').order_by('-created_at')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


# ==================== ADMIN PRODUCT CRUD ====================

class AdminProductCreateView(generics.CreateAPIView):
    """
    Create a new product (Admin only).
    POST /api/admin/products/
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminProductUpdateView(generics.UpdateAPIView):
    """
    Update a product by slug (Admin only).
    PATCH /api/admin/products/{product_slug}/
    PUT /api/admin/products/{product_slug}/
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'


class AdminProductDeleteView(generics.DestroyAPIView):
    """
    Delete a product by slug (Admin only - soft delete).
    DELETE /api/admin/products/{product_slug}/
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.is_active = False
        instance.save()


# ==================== ADMIN IMAGE MANAGEMENT ====================

class AdminProductImageAddView(APIView):
    """
    Add image URL to product (Admin only).
    POST /api/admin/products/{product_slug}/images/
    Body: {"image_url": "https://example.com/image.jpg"}
    """
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        serializer = ProductImageManagementSerializer(data=request.data)
        
        if serializer.is_valid():
            image_url = serializer.validated_data['image_url']
            
            # Check if image URL already exists
            if image_url in product.images:
                return Response(
                    {'error': 'Image URL already exists for this product.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add image URL to list
            product.images.append(image_url)
            product.save()
            
            return Response({
                'message': 'Image added successfully.',
                'images': product.images
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductImageDeleteView(APIView):
    """
    Remove image URL from product by index (Admin only).
    DELETE /api/admin/products/{product_slug}/images/{index}/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def delete(self, request, product_slug, index):
        product = get_object_or_404(Product, slug=product_slug)
        
        try:
            index = int(index)
            if index < 0 or index >= len(product.images):
                return Response(
                    {'error': 'Invalid image index.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Remove image at index
            removed_url = product.images.pop(index)
            product.save()
            
            return Response({
                'message': 'Image removed successfully.',
                'removed_url': removed_url,
                'images': product.images
            }, status=status.HTTP_200_OK)
        
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid index format.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminProductImageUpdateView(APIView):
    """
    Update image URL at specific index (Admin only).
    PATCH /api/admin/products/{product_slug}/images/{index}/
    Body: {"image_url": "https://example.com/new-image.jpg"}
    """
    permission_classes = [permissions.IsAdminUser]
    
    def patch(self, request, product_slug, index):
        product = get_object_or_404(Product, slug=product_slug)
        serializer = ProductImageManagementSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                index = int(index)
                if index < 0 or index >= len(product.images):
                    return Response(
                        {'error': 'Invalid image index.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update image at index
                old_url = product.images[index]
                new_url = serializer.validated_data['image_url']
                product.images[index] = new_url
                product.save()
                
                return Response({
                    'message': 'Image updated successfully.',
                    'old_url': old_url,
                    'new_url': new_url,
                    'images': product.images
                }, status=status.HTTP_200_OK)
            
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid index format.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProductImagesListView(APIView):
    """
    List all images for a product (Admin only).
    GET /api/admin/products/{product_slug}/images/
    """
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        
        return Response({
            'product_slug': product.slug,
            'product_name': product.name,
            'images': product.images,
            'image_count': len(product.images)
        }, status=status.HTTP_200_OK)


# ==================== PRODUCT REVIEWS ====================

class ProductReviewListView(generics.ListCreateAPIView):
    """
    List reviews for a product or create a new review.
    GET /api/products/{product_slug}/reviews/
    POST /api/products/{product_slug}/reviews/ (Authenticated users)
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductReview.objects.filter(
            product__slug=product_slug,
            is_approved=True
        ).select_related('user', 'product')
    
    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        serializer.save(user=self.request.user, product=product)


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific review.
    GET /api/products/{product_slug}/reviews/{review_id}/
    PATCH /api/products/{product_slug}/reviews/{review_id}/ (Review owner)
    DELETE /api/products/{product_slug}/reviews/{review_id}/ (Review owner or Admin)
    """
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductReview.objects.filter(product__slug=product_slug)
