"""Tags serializers."""
from rest_framework import serializers
from .models import Tag, ProductTag


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer."""
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'color', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']
    
    def get_product_count(self, obj):
        """Get count of products with this tag."""
        return obj.tagged_products.count()


class ProductTagSerializer(serializers.ModelSerializer):
    """Product-Tag relationship serializer."""
    
    tag = TagSerializer(read_only=True)
    tag_id = serializers.UUIDField(write_only=True)
    product_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = ProductTag
        fields = ['id', 'product', 'product_id', 'tag', 'tag_id', 'added_at']
        read_only_fields = ['id', 'added_at']
