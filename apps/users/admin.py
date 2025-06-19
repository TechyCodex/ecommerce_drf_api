from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cart, CartItem, CustomUser, Address, CustomerUser, AdminUser

# 🧠 Common user admin base
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

# ✅ Customer admin
@admin.register(CustomerUser)
class CustomerUserAdmin(CustomUserBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='customer').exclude(is_superuser=True)

# ✅ Admin user admin
@admin.register(AdminUser)
class AdminUserAdmin(CustomUserBaseAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='admin').exclude(is_superuser=True)

    def save_model(self, request, obj, form, change):
        obj.user_type = 'admin'
        super().save_model(request, obj, form, change)

# ✅ Address admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'address_line1', 'address_line2', 'city',
        'state', 'postal_code', 'country', 'is_default'
    )
    search_fields = ('address_line1', 'city', 'state', 'postal_code', 'country', 'user__email')

# ✅ Cart admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email',)

# ✅ Cart Item admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('product__name',)

# ✅ Panel branding
admin.site.index_title = "TechyCart Admin"
admin.site.site_header = "TechyCart Admin Panel"
admin.site.site_title = "TechyCart"
