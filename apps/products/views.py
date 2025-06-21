from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes

from apps.users.views import User
from .models import Product,Category, Review
from .serializers import ProductDetailSerializer,ProductListSerializer,CategoryDetailSerializer,CategoryListSerializer, ReviewSerializer

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



# This view handles POST requests to add a review for a product
@api_view(['POST'])
def add_review(request):
    
    product_id = request.data.get('product_id')
    email = request.data.get('email')
    rating = request.data.get('rating')
   
    review_text = request.data.get('review')
    
    product = Product.objects.get(id=product_id)
    user = User.objects.get(email=email)
    
    if Review.objects.filter(product=product,user=user).exists():
        return Response('You already dropped a review for this product',status=400)
    
    review = Review.objects.create(
        product=product,
        user=user,
        rating=rating,
        review=review_text
    )
    serializer = ReviewSerializer(review)
    return Response({"data": serializer.data, "message": "Review added successfully"})

@api_view(['PUT'])
def update_review(request,pk):
    review = Review.objects.get(id=pk)
    rating = request.data.get('rating')
    review_text = request.data.get('review')
    
    review.rating = rating
    review.review = review_text
    review.save()
    
    serializer = ReviewSerializer(review)
    return Response({"data": serializer.data, "message": "Review updated successfully"})



@api_view(['DELETE'])
def delete_review(request,pk):
    review = Review.objects.get(id=pk)
    review.delete()
    
    return Response('Review deleted Successfully',status=200)

   