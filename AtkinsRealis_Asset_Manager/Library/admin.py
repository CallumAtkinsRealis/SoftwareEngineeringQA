from django.contrib import admin
from .models import CustomUser, AssetBooking

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(AssetBooking)
