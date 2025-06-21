from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_img', blank=True, null=True)
    
    
    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # ...rest of your code...
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True,blank=True,)
    image_url = models.ImageField(upload_to='product_img', blank=True, null=True)
    featured = models.BooleanField(default=False)
    Category = models.ForeignKey(Category, related_name='products',on_delete=models.SET_NULL, blank=True, null=True)
    
    
    def __str__(self):
        return self.name
    # This method generates a unique slug for the product based on its name
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)



class Review(models.Model):
    
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)
    review = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created']
    
    
class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating')
    average_rating = models.FloatField(default=0.00)    
    total_reviews = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.product.name} - {self.average_rating} Total Reviews: {self.total_reviews}"
    
            