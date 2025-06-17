from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('add-address/', views.add_address, name='add_address'),
    path('update-address/<int:pk>/', views.update_address, name='update_address'),
    path('request-reset-password/', views.request_password_reset, name='request-reset-password'),
    path('reset-password/', views.reset_password_form, name='reset-password-form'),
    path('reset-password/submit/', views.reset_password_submit, name='reset-password-submit'),
    path('upload-profile-image/', views.upload_profile_image, name='upload-profile-image'),

]