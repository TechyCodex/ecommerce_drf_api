from django.contrib import admin
from .models import Product,Category, ProductRating, Review

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'featured',)
    
admin.site.register(Product,ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
admin.site.register(Category, CategoryAdmin)  



admin.site.register([ Review, ProductRating]) 