from django.urls import path
from . import views
urlpatterns = [
    path('products_list/', views.product_list, name='product_list'),  # <-- trailing slash
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),  # <-- trailing slash
    path('category_list/', views.category_list, name='category_list'),  # <-- trailing slash
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),  # <-- trailing slash
]