from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    AddressSerializer,
    ProfileImageUploadSerializer,
    UserRegisterSerializer,
    CartItemSerializer,
    CartSerializer
)
from utils.email_functions import send_verification_email
from .models import Address,Cart,CartItem
from products.models import Product

import threading
import uuid
import os

User = get_user_model()

# ✅ Registration API
@api_view(['POST'])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        verification_token = str(uuid.uuid4())
        user.verification_token = verification_token
        user.is_verified = False
        user.save()

        verification_link = f"http://192.168.31.176:8080/api/users/verify-email/?token={verification_token}"

        threading.Thread(
            target=send_verification_email,
            args=(user, verification_link)
        ).start()

        return Response({'message': 'Registration successful. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Login API
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        user.token = access_token
        user.save()
        return Response({
            'data': UserRegisterSerializer(user).data,
            'token': access_token
        })
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ Email Verification API
@api_view(['GET'])
def verify_email(request):
    token = request.GET.get('token')
    try:
        user = User.objects.get(verification_token=token)
        user.is_verified = True
        user.verification_token = None
        user.save()
        return render(request, 'email/email_verified.html')
    except User.DoesNotExist:
        return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

# ✅ Add Address API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer = AddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'message': 'Address added successfully!', 'address': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Update Address API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_address(request, pk):
    try:
        address = Address.objects.get(pk=pk, user=request.user)
    except Address.DoesNotExist:
        return Response({'error': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = AddressSerializer(address, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Address updated successfully!', 'address': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Request Password Reset API
@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token = str(uuid.uuid4())
        user.verification_token = token
        user.save()

        reset_link = f"http://192.168.31.176:8080/api/users/reset-password/?token={token}"
        subject = "Reset Your TechyCart Password"
        message = f"Hi {user.username},\n\nClick below to reset your password:\n{reset_link}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        
        return Response({'message': 'Reset link sent to email.'}, status=200)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist.'}, status=404)

# ✅ Reset Password Form View
def reset_password_form(request):
    token = request.GET.get('token', '')
    return render(request, 'reset_password.html', {'token': token})

# ✅ Reset Password Submission
@csrf_exempt
@api_view(['POST'])
def reset_password_submit(request):
    token = request.POST.get('token')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=400)

    try:
        user = User.objects.get(verification_token=token)
        user.set_password(password)
        user.verification_token = ''
        user.save()
        return render(request, 'reset_success.html')
    except User.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=400)

# ✅ Profile Image Upload API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_image(request):
    serializer = ProfileImageUploadSerializer(data=request.data)
    if serializer.is_valid():
        image = serializer.validated_data['image']
        user = request.user

        folder_path = os.path.join(settings.MEDIA_ROOT, 'profile_pics')
        os.makedirs(folder_path, exist_ok=True)
        filename = f"{user.id}_{image.name}"
        image_path = os.path.join(folder_path, filename)

        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        image_url = settings.MEDIA_URL + 'profile_pics/' + filename
        full_url = request.build_absolute_uri(image_url)
        user.profile_picture_url = full_url
        user.save()

        return Response({'profile_picture_url': full_url}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def add_to_cart(request):
    cart_code = request.data.get('cart_code')
    product_id = request.data.get('product_id')

    cart, _ = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)

    cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cartitem.quantity = 1  # Set to 1 if new cart item
    else:
        cartitem.quantity += 1  # Increment if already exists
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response({"data":serializer.data, "message": "Cart item added successfully"})

# This view handles PUT requests to update the quantity of a cart item
@api_view(['PUT'])
def update_cart_item(request):
    Cartitem_id = request.data.get('item_id')
    quantity = request.data.get('quantity')
    
    quantity = int(quantity)
    
    Cartitem = CartItem.objects.get(id=Cartitem_id)
    Cartitem.quantity = quantity
    Cartitem.save()
    
    serializer = CartItemSerializer(Cartitem)
    return Response({"data":serializer.data, "message": "Cart item updated successfully"})




@api_view(['DELETE'])
def delete_cartitem(request,pk):
    review = CartItem.objects.get(id=pk)
    review.delete()
    
    return Response('CartItem deleted Successfully',status=200)
