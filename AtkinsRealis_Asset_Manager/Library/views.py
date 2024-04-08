from django.http import HttpResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Q
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
def usermanage(request):
    # Fetch all users from CustomUser model
    myusers = CustomUser.objects.all().values()

    # Hides all passwords as 12 x *
    for user in myusers:
        user['password'] = '*' * 12

    context = { 
            "myusers" : myusers,
        } 
    # Renders usermanage page with all users
    return render(request, "user_manage.html", context)

@login_required
def create(request):
    # checks the form submitted on the create_user page
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                #Save User in CustomUser Model
                CustomUserSave = form.save()
                messages.success(request, 'User created successfully.')
                # Redirect to usermanage on successful submission
                return redirect('usermanage')
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def delete_user(request, email):
    # renders the delete_user page 
    # Checks to see if the user is_staff and can delete the user
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('usermanage')
    
    # Get the user object or return a 404 error if not found
    user = get_object_or_404(CustomUser, email=email)
    
    if request.method == 'POST':
        # Update email to empty string for associated bookings where the user is referenced
        AssetBooking.objects.filter(Q(booked_by=user) | Q(project_manager=user)).update(
            booked_by=None, 
            project_manager=None
            )

        # Now delete the user itself
        user.delete()

        messages.success(request, 'User deleted successfully.')

    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('usermanage')  # Redirect to a page that lists all users after deletion

@login_required
def info(request):
    # renders the user page 
    user = request.user
    try:
        custom_user = CustomUser.objects.get(email=user)
        if request.method == 'POST':
            form = CustomUserForm(request.POST, instance=custom_user)
            if form.is_valid():
                form.save()
                messages.success(request, 'User information updated successfully.')
                return redirect('usermanage')  # Redirect to the same page after successful update
            else:
                messages.error(request, 'Error updating user information. Please check the form.')
        else:
            form = CustomUserForm(instance=custom_user)  # Pass the user instance to prepopulate the form fields
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('usermanage')

    return render(request, 'user_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def user_update(request, username):
        # Checks to see if the user is_staff and can update the user
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('usermanage')
    
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
            return redirect('usermanage')  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Error updating user information. Please check the form.')
    else:
        form = CustomUserForm(instance=user)  # Pass the user instance to prepopulate the form fields

    return render(request, 'user_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def bookingmanage(request):
    # Fetch all bookings from CustomUser model
    mybookings = AssetBooking.objects.all().values()
    myusers = CustomUser.objects.all().values()

    context = { 
            "mybookings" : mybookings,
            "myusers" : myusers
        } 
    return render(request, "bookings_manage.html", context)

@login_required
def assetbooking(request):
    if request.method == 'POST':
        form = AssetBookingForm(request.POST)
        if form.is_valid():
            messages.success(request, 'New booking created successfully.')
            form.save()
            # Redirect to a success URL or render a success message
            return redirect('bookingmanage')
        else:
            messages.error(request, 'Error creating new booking. Please check the form.')
            print("Form is invalid:", form.errors)  # Print form errors for debugging
    else:
        form = AssetBookingForm()
    return render(request, 'new_booking.html', {'form': form})

@login_required
def booking_update(request, booking_id):
    existing_booking = get_object_or_404(AssetBooking, booking_id=booking_id)

    if request.method == 'POST':
        form = AssetBookingForm(request.POST, instance=existing_booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking information updated successfully.')
            return redirect('bookingmanage')  # Redirect to the same page after successful update
        else:
            messages.error(request, 'Error updating booking information. Please check the form.')
    else:
        form = AssetBookingForm(instance=existing_booking)  # Pass the booking instance to prepopulate the form fields

    return render(request, 'booking_info.html', {'form': form, 'error_messages': messages.get_messages(request)})


@login_required
def delete_booking(request, booking_id):
    if not request.user.is_staff:
        messages.error(request, 'Sorry, you do not have permissions to do that.')
        return redirect('bookingmanage')
    
    # Get the booking object or return a 404 error if not found
    booking = get_object_or_404(AssetBooking, booking_id=booking_id)
    
    if request.method == 'POST':
        # Delete instances from Assetbooking where the booking_id is referenced
        AssetBooking.objects.filter(booking_id=booking_id).delete()
        
        messages.success(request, 'Booking deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('bookingmanage')

def login_request(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Assuming 'username' field is used for email input
            password = form.cleaned_data.get('password')
            user = authenticate_custom_user(email=email, password=password)
            if user is not None:
                if user.is_active:  # Ensure user account is active
                    login(request, user)
                    print("User logged in:", user)  # Debugging statement
                    return redirect('/home_page')  # Redirect to some page after login
                else:
                    print("Inactive user:", user)  # Debugging statement
                    messages.error(request, 'Your account is inactive.')
            else:
                print("Invalid credentials for email:", email)  # Debugging statement
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'login_page.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                custom_user = form.save()  # Save user in CustomUser model
                messages.success(request, 'User created successfully.')
                return redirect('login')  # Redirect to login page on successful submission
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form, 'error_messages': messages.get_messages(request)})

def authenticate_custom_user(email, password):
    try:
        user = CustomUser.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            return None
    except CustomUser.DoesNotExist:
        return None

def logout_request(request):
    logout(request)
    return redirect('login')
