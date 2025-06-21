# orders/serializers.py
from rest_framework import serializers

from apps.users.serializers import AddressSerializer
from .models import Order, OrderItem
from apps.products.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_code', 'total_price', 'status', 'created_at', 'address', 'items']
