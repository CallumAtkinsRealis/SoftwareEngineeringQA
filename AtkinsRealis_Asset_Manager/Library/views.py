from django.http import HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .forms import LoginForm, CustomUserForm, CustomUserCreationForm, AssetBookingForm
from .models import CustomUser, AssetBooking

# Create your views here.

@login_required
def default(request):
    return redirect('login')

@login_required
def home(request):
    # Renders home page
    return render(request, "home.html")

@login_required
def user_page(request):
    # Fetch all users from CustomUser model
    myusers = CustomUser.objects.all().values()

    # Hides all passwords as 12 x *
    for user in myusers:
        user['password'] = '*' * 12

    context = { 
            "myusers" : myusers,
        } 
    # Renders user_page page with all users
    return render(request, "user_manage.html", context)

@login_required
def create_user(request):
    # checks the form submitted on the create_user page
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                #Save User in CustomUser Model
                CustomUserSave = form.save()
                messages.success(request, 'User created successfully.')
                # Redirect to user_page on successful submission
                return redirect('user_page')
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def delete_user(request, email):
    # Get the user object or return a 404 error if not found
    user = get_object_or_404(CustomUser, email=email)
    
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('user_page')

    if request.method == 'POST':
        # Update email to empty string for associated bookings where the user is referenced
        AssetBooking.objects.filter(Q(booked_by=user) | Q(project_manager=user)).update(
            booked_by=None, 
            project_manager=None
        )

        # Now delete the user itself
        user.delete()

        messages.success(request, 'User deleted successfully.')
        return redirect('user_page')

    # Render a confirmation page for GET requests
    return render(request, 'confirm_delete.html', {'user': user})

@login_required
def user_info(request):
    # renders the user page 
    user = request.user
    try:
        custom_user = CustomUser.objects.get(email=user)
        if request.method == 'POST':
            form = CustomUserForm(request.POST, instance=custom_user)
            if form.is_valid():
                form.save()
                messages.success(request, 'User information updated successfully.')
                return redirect('user_page')  # Redirect to the same page after successful update
            else:
                messages.error(request, 'Error updating user information. Please check the form.')
        else:
            form = CustomUserForm(instance=custom_user)  # Pass the user instance to prepopulate the form fields
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_page')

    return render(request, 'user_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def user_update(request, username):
        # Checks to see if the user is_staff and can update the user
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('user_page')
    
    # Get the user object or return a 404 error if not found
    user = get_object_or_404(CustomUser, email=username)

    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            # Check if password field is empty, if not, update the password
            if not form.cleaned_data['password']:
                form.cleaned_data.pop('password')  # Remove the password field from cleaned data
            form.save()
            messages.success(request, 'User information updated successfully.')
            return redirect('user_page')  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Error updating user information. Please check the form.')
    else:
        form = CustomUserForm(instance=user)  # Pass the user instance to prepopulate the form fields

    return render(request, 'user_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def booking_page(request):
    # Fetch all bookings from CustomUser model
    mybookings = AssetBooking.objects.all().values()
    myusers = CustomUser.objects.all().values()

    context = { 
            "mybookings" : mybookings,
            "myusers" : myusers
        } 
    return render(request, "bookings_manage.html", context)

@login_required
def create_booking(request):
    # Renders the create_booking FORM to booking_page URL
    if request.method == 'POST':
        form = AssetBookingForm(request.POST)
        if form.is_valid():
            messages.success(request, 'New booking created successfully.')
            form.save()
            # Redirect to booking_page URL
            return redirect('booking_page')
        else:
            messages.error(request, 'Error creating new booking. Please check the form.')
            print("Form is invalid:", form.errors)  # Print form errors for debugging
    else:
        form = AssetBookingForm()
    return render(request, 'new_booking.html', {'form': form})

@login_required
def booking_update(request, booking_id):
    # Renders the booking update page
    existing_booking = get_object_or_404(AssetBooking, booking_id=booking_id)

    # checks the submitted form
    if request.method == 'POST':
        form = AssetBookingForm(request.POST, instance=existing_booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking information updated successfully.')
            return redirect('booking_page')  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Error updating booking information. Please check the form.')
    else:
        form = AssetBookingForm(instance=existing_booking)  # Pass the booking instance to prepopulate the form fields

    return render(request, 'booking_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def booking_delete(request, booking_id):
    # Get the booking object or return a 404 error if not found
    booking = get_object_or_404(AssetBooking, booking_id=booking_id)
    
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('booking_page')

    if request.method == 'POST':
        # Delete instances from AssetBooking where the booking_id is referenced
        AssetBooking.objects.filter(booking_id=booking_id).delete()
        
        messages.success(request, 'Booking deleted successfully.')
        return redirect('booking_page')

    # Render a confirmation page for GET requests
    return render(request, 'confirm_delete_booking.html', {'booking': booking})

def login_request(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate_custom_user(email=email, password=password)
            ip = get_client_ip(request)
            key = f'failed_login_attempts_{ip}'
            attempts, first_attempt_time = cache.get(key, (0, None))
            
            if attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                return redirect('lockout_timer')
            else:
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        cache.delete(key)  # Reset attempts on successful login
                        print("User logged in:", user)
                        return redirect('/home_page')
                    else:
                        print("Inactive user:", user)
                        messages.error(request, 'Your account is inactive.')
                else:
                    if attempts == 0:
                        first_attempt_time = timezone.now()
                    attempts += 1
                    cache.set(key, (attempts, first_attempt_time), timeout=settings.FAILED_LOGIN_LOCK_DURATION)
                    print("Invalid credentials for email:", email)
                    messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'login_page.html', {'form': form})

def lockout_timer_view(request):
    ip = get_client_ip(request)
    key = f'failed_login_attempts_{ip}'
    attempts, first_attempt_time = cache.get(key, (0, None))
    if first_attempt_time:
        lockout_time = settings.FAILED_LOGIN_LOCK_DURATION - (timezone.now() - first_attempt_time).total_seconds()
        if lockout_time <= 0:
            return redirect('login')  # Redirect to login page if lockout period is over
    else:
        lockout_time = 0
    return render(request, 'lockout.html', {'lockout_time': lockout_time})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')

            if not password:
                messages.error(request, 'Password field is empty.')
                return render(request, 'register.html', {'form': form})

            try:
                validate_password(password)
            except ValidationError as e:
                form.add_error('password', e)  # Add validation error to the password field
                messages.error(request, 'Your password must be between 8-20 characters and include at least one special character.')
            else:
                with transaction.atomic():
                    custom_user = form.save()
                    messages.success(request, 'User created successfully.')
                    return redirect('login')
        else:
            messages.error(request, 'Error creating user. Please check the form.')

        # Re-render the form with entered data, including errors, but without clearing any field
        return render(request, 'register.html', {'form': form})

    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def authenticate_custom_user(email, password):
    # function for authenticating custom user
    try:
        user = CustomUser.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            return None
    except CustomUser.DoesNotExist:
        return None
    
def confirm_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'confirm_logout.html')

def logout_request(request):
    return redirect('confirm_logout')
