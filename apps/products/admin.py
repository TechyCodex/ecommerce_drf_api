from django.contrib import admin
from .models import Product,Category, ProductRating, Review

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'featured',)
    list_editable = ('featured',)  # You can edit directly from the list
    list_filter = ('featured',)    # Filter products by featured status
    
admin.site.register(Product,ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
admin.site.register(Category, CategoryAdmin)  



admin.site.register([ Review, ProductRating]) 