from django.urls import path
from django.contrib import admin
from . import views

# Create your urls here.

urlpatterns = [
    path('login/', views.login, name='login'),
    path('home_page/', views.home, name='home'),
]