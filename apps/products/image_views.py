"""Product Image views."""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from apps.products.models import Product, ProductImage
from apps.products.image_serializers import (
    ProductImageSerializer,
    ProductImageCreateSerializer,
    ProductImageUpdateSerializer
)


class ProductImageListView(generics.ListCreateAPIView):
    """List and create product images."""
    
    serializer_class = ProductImageSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductImage.objects.filter(product_id=product_id).order_by('display_order')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductImageCreateSerializer
        return ProductImageSerializer
    
    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        
        # If this is the first image, make it primary
        if not ProductImage.objects.filter(product=product).exists():
            serializer.save(product=product, is_primary=True)
        else:
            serializer.save(product=product)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product image (admin only for update/delete)."""
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductImageUpdateSerializer
        return ProductImageSerializer
    
    def get_object(self):
        """Get image by product_id and image_id."""
        product_id = self.kwargs['product_id']
        image_id = self.kwargs['image_id']
        return get_object_or_404(ProductImage, id=image_id, product_id=product_id)
    
    def perform_destroy(self, instance):
        """Handle primary image deletion."""
        product = instance.product
        was_primary = instance.is_primary
        
        instance.delete()
        
        # If deleted image was primary, set another image as primary
        if was_primary:
            remaining_images = ProductImage.objects.filter(product=product).order_by('display_order').first()
            if remaining_images:
                remaining_images.is_primary = True
                remaining_images.save()


@api_view(['POST'])
@permission_classes([IsAdminUser])
def set_primary_image(request, product_id, image_id):
    """Set an image as the primary image for a product."""
    try:
        product = Product.objects.get(id=product_id)
        image = ProductImage.objects.get(id=image_id, product=product)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ProductImage.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Unset other primary images for this product
    ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
    
    # Set this image as primary
    image.is_primary = True
    image.save()
    
    return Response({
        'success': True,
        'message': 'Primary image updated successfully',
        'image': ProductImageSerializer(image).data
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reorder_images(request, product_id):
    """Reorder product images."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Expect array of {id, display_order}
    image_orders = request.data.get('images', [])
    
    if not image_orders:
        return Response(
            {'success': False, 'message': 'images array is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update display orders
    for item in image_orders:
        image_id = item.get('id')
        display_order = item.get('display_order')
        
        if image_id and display_order is not None:
            try:
                image = ProductImage.objects.get(id=image_id, product=product)
                image.display_order = display_order
                image.save(update_fields=['display_order'])
            except ProductImage.DoesNotExist:
                continue
    
    # Return updated images
    updated_images = ProductImage.objects.filter(product=product).order_by('display_order')
    serializer = ProductImageSerializer(updated_images, many=True)
    
    return Response({
        'success': True,
        'message': 'Images reordered successfully',
        'images': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_upload_images(request, product_id):
    """Bulk upload multiple images for a product."""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    images_data = request.data.get('images', [])
    
    if not images_data:
        return Response(
            {'success': False, 'message': 'images array is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_images = []
    errors = []
    
    # Get the highest display_order
    max_order = ProductImage.objects.filter(product=product).count()
    
    for idx, image_data in enumerate(images_data):
        serializer = ProductImageCreateSerializer(data=image_data)
        
        if serializer.is_valid():
            # Set display_order automatically
            image = serializer.save(
                product=product,
                display_order=max_order + idx
            )
            created_images.append(ProductImageSerializer(image).data)
        else:
            errors.append({
                'index': idx,
                'data': image_data,
                'errors': serializer.errors
            })
    
    return Response({
        'success': True,
        'message': f'{len(created_images)} images uploaded successfully',
        'created_count': len(created_images),
        'error_count': len(errors),
        'images': created_images,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_images else status.HTTP_400_BAD_REQUEST)
