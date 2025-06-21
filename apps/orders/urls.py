from django.urls import path
from . import views

urlpatterns = [
  path('place/', views.place_order, name='place_order'),
  path('order_now/', views.order_now, name='order_now'),
  path('list/', views.my_orders, name='my_orders'),
]