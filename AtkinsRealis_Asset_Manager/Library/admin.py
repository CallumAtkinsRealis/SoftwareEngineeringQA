from django.contrib import admin
from .models import CustomUser, AssetBooking

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')  # Add is_staff to the list display for visibility

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AssetBooking)
