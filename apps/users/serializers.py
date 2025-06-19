# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address,Cart,CartItem
from apps.products.serializers import ProductListSerializer

User = get_user_model()

class AddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'address_line1', 'address_line2', 'city',
            'state', 'postal_code', 'country', 'is_default'
        ]

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)
    fc_token = serializers.CharField(required=False, allow_blank=True)
    addresses = AddressSerializer(many=True, read_only=True)
    device_info = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'phone_number', 'fc_token', 'device_info', 'addresses', 'user_type'
        ]

    def create(self, validated_data):
        validated_data['user_type'] = 'customer'
        password = validated_data.pop('password')
        username = validated_data.get('username', '').strip()
        first_name = validated_data.get('first_name', '').strip().lower()
        last_name = validated_data.get('last_name', '').strip().lower()

        if not username:
            base_username = (first_name + last_name).replace(' ', '')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        validated_data['username'] = username

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
class ProfileImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    
    
    
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True) # Serializing product details in cart item
    sub_total = serializers.SerializerMethodField() # Calculating sub-total for each cart item
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_total'] 
        
    def get_sub_total(self, cartitem):
        total =  cartitem.quantity * cartitem.product.price
        return total
        
# Cart Serializer       
class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(many=True, read_only=True) # Serializing cart items
    cart_total = serializers.SerializerMethodField() # Calculating total for the cart
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'cartitems','cart_total']
        
    def get_cart_total(self, cart):
        items = cart.cartitems.all()
        total = sum([  item.quantity * item.product.price for item in items])   
        return total    

class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()  # Calculating total quantity of items in the cart
    class Meta:
        model = Cart
        fields = ['id', 'cart_code', 'total_quantity']  # Fields to be included in the serialized data     
        
    def get_total_quantity(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity for item in items])
        return total
    
    