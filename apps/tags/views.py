"""Tags views for the e-commerce platform."""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .models import Tag, ProductTag
from .serializers import TagSerializer, ProductTagSerializer
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer


class TagListView(generics.ListCreateAPIView):
    """List all tags or create a new tag (admin only)."""
    
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a tag (admin only for update/delete)."""
    
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


@api_view(['GET'])
@permission_classes([AllowAny])
def products_by_tag(request, tag_slug):
    """Get all products with a specific tag."""
    tag = get_object_or_404(Tag, slug=tag_slug, is_active=True)
    
    # Get all products with this tag
    product_tags = ProductTag.objects.filter(tag=tag).select_related('product')
    products = [pt.product for pt in product_tags if pt.product.is_active and not pt.product.is_deleted]
    
    # Apply pagination
    page = request.query_params.get('page', 1)
    limit = int(request.query_params.get('limit', 20))
    
    start_idx = (int(page) - 1) * limit
    end_idx = start_idx + limit
    
    paginated_products = products[start_idx:end_idx]
    
    serializer = ProductListSerializer(paginated_products, many=True)
    
    return Response({
        'success': True,
        'tag': TagSerializer(tag).data,
        'products': serializer.data,
        'total': len(products),
        'page': int(page),
        'limit': limit,
        'total_pages': (len(products) + limit - 1) // limit
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_tag_to_product(request, product_id):
    """Assign a tag to a product (admin only)."""
    tag_id = request.data.get('tag_id')
    
    if not tag_id:
        return Response(
            {'success': False, 'message': 'tag_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
        tag = Tag.objects.get(id=tag_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Tag.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Tag not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already assigned
    if ProductTag.objects.filter(product=product, tag=tag).exists():
        return Response(
            {'success': False, 'message': 'Tag already assigned to product'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create product-tag relationship
    product_tag = ProductTag.objects.create(product=product, tag=tag)
    
    return Response({
        'success': True,
        'message': 'Tag assigned to product successfully',
        'product_tag': ProductTagSerializer(product_tag).data
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_tag_from_product(request, product_id, tag_id):
    """Remove a tag from a product (admin only)."""
    try:
        product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
        tag = Tag.objects.get(id=tag_id, is_active=True)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Tag.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Tag not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find and delete the product-tag relationship
    product_tag = ProductTag.objects.filter(product=product, tag=tag).first()
    
    if not product_tag:
        return Response(
            {'success': False, 'message': 'Tag not assigned to product'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    product_tag.delete()
    
    return Response({
        'success': True,
        'message': 'Tag removed from product successfully'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def product_tags(request, product_id):
    """Get all tags for a specific product."""
    try:
        product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    product_tags = ProductTag.objects.filter(product=product).select_related('tag')
    tags = [pt.tag for pt in product_tags if pt.tag.is_active]
    
    serializer = TagSerializer(tags, many=True)
    
    return Response({
        'success': True,
        'product_id': str(product.id),
        'product_name': product.name,
        'tags': serializer.data,
        'total': len(tags)
    })

