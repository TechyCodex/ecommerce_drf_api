from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .models import Product,Category
from .serializers import ProductDetailSerializer,ProductListSerializer,CategoryDetailSerializer,CategoryListSerializer

# Create your views here.
## These views handle API requests for products and categories, returning serialized data.
@api_view(['GET'])
# This view handles GET requests to fetch a list of all products
def product_list(request):
    products = Product.objects.all()  # Fetching all products from the database
    serializer = ProductListSerializer(products, many=True) # Serializing the product data
    return Response(serializer.data) # Returning serialized product data as a response

@api_view(['GET'])
# This view handles GET requests to fetch details of a specific product by slug
def product_detail(request, slug):
    
    try:
        Product = Product.objects.get(slug=slug)  # Fetching product by slug
        serializer = ProductDetailSerializer(Product) # Serializing the product data
        return Response(serializer.data) # Returning serialized product data as a response
    except Product.DoesNotExist: # Handling case where product does not exist
        return Response({'error': 'Product not found'}, status=404) # Handling case where product does not exist
    
    
@api_view(['GET'])
# This view handles GET requests to fetch a list of all categories
def category_list(request):
    categories = Category.objects.all()  # Fetching all categories from the database
    serializer = CategoryListSerializer(categories, many=True)  # Serializing the categories        
    return Response(serializer.data)    # Returning the serialized data as a response


@api_view(['GET'])
# This view handles GET requests to fetch details of a specific category by slug
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug)  # Fetching category by slug
        serializer = CategoryDetailSerializer(category)  # Serializing the category data
        return Response(serializer.data)  # Returning serialized category data as a response
    except Category.DoesNotExist:   # Handling case where category does not exist
        return Response({'error': 'Category not found'}, status=404)
   