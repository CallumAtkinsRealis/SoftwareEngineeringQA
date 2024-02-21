from django.urls import path
from django.contrib import admin
from . import views

# Create your urls here.

urlpatterns = [
    path('', views.default, name='default'),
    path('login/', views.login_request, name='login'),
    path('home_page/', views.home, name='home'),
    path('create_user/', views.create, name='create'),
]