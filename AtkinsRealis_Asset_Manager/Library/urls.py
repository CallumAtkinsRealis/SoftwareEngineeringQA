from django.urls import path
from django.contrib import admin
from . import views

# Create your urls here.

urlpatterns = [
    # User URLs
    path('', views.default, name='default'),
    path('login/', views.login_request, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_request, name='logout'),
    path('home_page/', views.home, name='home'),
    path('create_user/', views.create_user, name='create_user'),
    path('delete_user/<str:email>/', views.delete_user, name='delete_user'),
    path('user_info/', views.user_info, name='user_info'),
    path('user_update/<str:username>/', views.user_update, name='user_update'),
    path('user_manage/', views.user_page, name='user_page'),
    
    # Booking URLs
    path('booking_page/', views.booking_page, name='booking_page'),
    path('booking_update/<str:booking_id>/', views.booking_update, name='booking_update'),
    path('new_booking/', views.create_booking, name='create_booking'),
    path('booking_delete/<str:booking_id>/', views.booking_delete, name='booking_delete'),
]
