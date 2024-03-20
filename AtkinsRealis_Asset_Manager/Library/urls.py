from django.urls import path
from django.contrib import admin
from . import views

# Create your urls here.

urlpatterns = [
    path('', views.default, name='default'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('home_page/', views.home, name='home'),
    path('create_user/', views.create, name='create'),
    path('delete_user/<str:email>/', views.delete_user, name='delete_user'),
    path('user_info/', views.info, name='info'),
    path('user_manage/', views.usermanage, name='usermanage'),
    path('booking_manage/', views.bookingmanage, name='bookingmanage'),
    path('new_booking/', views.assetbooking, name='newbooking'),
    path('delete_booking/<str:booking_id>/', views.delete_booking, name='delete_booking'),
]