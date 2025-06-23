from django.urls import path
from . import views
urlpatterns = [
    path('products_list/', views.product_list, name='product_list'),  # <-- trailing slash
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),  # <-- trailing slash
    path('category_list/', views.category_list, name='category_list'),  # <-- trailing slash
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),  # <-- trailing slash
    path('add_review/', views.add_review, name='add_review'),
    path('update_review/<int:pk>/',views.update_review, name='update_review'),
    path('delete_review/<int:pk>/',views.delete_review, name='delete_review'),
    path('featured/', views.featured_products, name='featured-products'),
]