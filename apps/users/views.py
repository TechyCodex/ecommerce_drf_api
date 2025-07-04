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
from utils.notification import send_firebase_notification_v1


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserRegisterSerializer



from .serializers import (
    AddressSerializer,
    ProfileImageUploadSerializer,
    UserRegisterSerializer,
    CartItemSerializer,
    CartSerializer
)
from utils.email_functions import send_verification_email
from .models import Address,Cart,CartItem
from apps.products.models import Product

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

        verification_link = request.build_absolute_uri(f"/api/users/verify-email/?token={verification_token}")

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

    # ✅ Input validation
    if not email or not password:
        return Response(
            {'error': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Authenticate user
    user = authenticate(request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Optional: If you have `token` field in user model
        user.token = access_token
        user.save()

        return Response({
            'data': UserRegisterSerializer(user).data,
            'token': access_token
        })

    return Response(
        {'error': 'Invalid credentials. Please check your email and password.'},
        status=status.HTTP_401_UNAUTHORIZED
    )

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

        reset_link = request.build_absolute_uri(f"/api/users/reset-password/?token={token}")

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
    product_id = request.data.get('product_id')

    if not product_id:
        return Response({'error': 'Product ID is required'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=404)

    # Get or create cart by user
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cartitem.quantity += 1
    cartitem.save()

    serializer = CartSerializer(cart)
    return Response({"data": serializer.data, "message": "Cart item added successfully"})


# This view handles PUT requests to update the quantity of a cart item
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')

    if not item_id or quantity is None:
        return Response({'error': 'Item ID and quantity are required'}, status=400)

    try:
        quantity = int(quantity)
        if quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=400)
    except ValueError:
        return Response({'error': 'Quantity must be a valid integer'}, status=400)

    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)

    cart_item.quantity = quantity
    cart_item.save()

    serializer = CartItemSerializer(cart_item)
    return Response({"data": serializer.data, "message": "Cart item updated successfully"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cartitem(request, pk):
    try:
        cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=404)

    cart_item.delete()
    return Response({'message': 'Cart item deleted successfully'}, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({"message": "Cart is empty", "data": []}, status=200)

    serializer = CartSerializer(cart)
    return Response({"data": serializer.data, "message": "Cart fetched successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification_to_user(request):
    user_id = request.data.get('user_id')
    title = request.data.get('title')
    body = request.data.get('body')

    try:
        user = User.objects.get(id=user_id)
        if user.fc_token:
            result = send_firebase_notification_v1(user.fc_token, title, body)
            return Response({'success': True, 'message_id': result})
        else:
            return Response({'error': 'User does not have an FCM token'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    