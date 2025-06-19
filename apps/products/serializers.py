from rest_framework import serializers
from .models import Product,Category


# Product List Serializer
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'slug', 'image_url']
         

# Product Detail Serializer
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'slug', 'image']
        
        
        
# Category List Serializer        
class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug']          
                
# Category Serializer        
class CategoryDetailSerializer(serializers.ModelSerializer):
    Products = ProductListSerializer(many=True, read_only=True) # Serializing products in category
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image','products']         
