# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address

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