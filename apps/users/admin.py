# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address, CustomerUser, AdminUser

# Base admin for shared fields
class CustomUserBaseAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'phone_number', 'fc_token', 'device_info', 'profile_picture_url',
                'user_type', 'verification_token', 'token'
            ),
        }),
    )

# ✅ Register proxy: Customers only
@admin.register(CustomerUser)
class CustomerUserAdmin(CustomUserBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='customer').exclude(is_superuser=True)


# ✅ Register proxy: Admin users only
@admin.register(AdminUser)
class AdminUserAdmin(CustomUserBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='admin').exclude(is_superuser=True)

    def save_model(self, request, obj, form, change):
        # Ensure user_type is set to 'admin'
        obj.user_type = 'admin'
        super().save_model(request, obj, form, change)

# ✅ Register Address normally
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'address_line1', 'address_line2', 'city',
        'state', 'postal_code', 'country', 'is_default'
    )
    search_fields = ('address_line1', 'city', 'state', 'postal_code', 'country', 'user__email')
