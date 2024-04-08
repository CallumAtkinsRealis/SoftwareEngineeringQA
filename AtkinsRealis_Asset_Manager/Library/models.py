from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

#User = get_user_model()

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff_linked=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    job_title = models.CharField(max_length=100)
    password_creation_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Custom related names for groups and user_permissions
    groups = models.ManyToManyField(Group, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'job_title']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class AssetBooking(models.Model):

    BOOKING_ID_CHOICES = (
        ('CAM', 'Camera'),
        ('LAS', 'Laser Scanner'),
        ('VRH', 'VR Headset'),
        ('ARH', 'AR Headset'),
        ('ROB', 'Robot'),
    )

    booking_id = models.AutoField(primary_key=True)
    booked_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='bookings_as_booked_by', null=True, default='')
    asset_category = models.CharField(max_length=3, choices=BOOKING_ID_CHOICES)
    asset_name = models.CharField(max_length=100)
    asset_id = models.CharField(max_length=100)
    project_name = models.CharField(max_length=255)
    project_number = models.CharField(max_length=20)
    project_manager = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, null=True, default='')
    date_booked_for = models.DateField()
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Logic to automatically fill asset_id based on the selected asset category and name
        if not self.asset_id:  # Only fill if not already set
            self.asset_id = f"{self.asset_category}-{self.asset_name}"  # Example logic, adjust as needed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking ID: {self.booking_id}, Asset: {self.asset_name}, Project: {self.project_name}"