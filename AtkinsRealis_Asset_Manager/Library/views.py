from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, CustomUserForm, CustomUserCreationForm, AssetBookingForm
from .models import CustomUser, AssetBooking
from django.db import transaction
# Create your views here.

@login_required
def default(request):
    return redirect('login')

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

@login_required
def home(request):
    # Fetch all users from CustomUser model
    myusers = CustomUser.objects.all().values()
    mybookings = AssetBooking.objects.all().values()

    for user in myusers:
        user['password'] = '*' * 12

    context = { 
            "myusers" : myusers,
            "mybookings" : mybookings 
        } 
    return render(request, "home.html", context)

@login_required
def usermanage(request):
    # Fetch all users from CustomUser model
    myusers = CustomUser.objects.all().values()

    for user in myusers:
        user['password'] = '*' * 12

    context = { 
            "myusers" : myusers,
        } 
    return render(request, "user_manage.html", context)

@login_required
def create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                custom_user = form.save()  # Save user in CustomUser model
                # Create corresponding User object
                #user = User.objects.create_user(username=custom_user.username, email=custom_user.email, password=form.cleaned_data['password'])
                messages.success(request, 'User created successfully.')
                return redirect('home')  # Redirect to login page on successful submission
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def delete_user(request, email):
    user = get_object_or_404(User, email=email)
    
    # Delete instances from Model1 where the user is referenced
    User.objects.filter(email=email).delete()
    
    # Delete instances from Model2 where the user is referenced
    CustomUser.objects.filter(email=email).delete()
    
    # Now delete the user itself
    user.delete()
    
    return redirect('home')  # Redirect to a page that lists all users after deletion

@login_required
def info(request):
    user = request.user
    print(user)
    try:
        custom_user = CustomUser.objects.get(email=user)
        if request.method == 'POST':
            form = CustomUserForm(request.POST, instance=custom_user)
            if form.is_valid():
                form.save()
                messages.success(request, 'User information updated successfully.')
                return redirect('info')  # Redirect to the same page after successful update
            else:
                messages.error(request, 'Error updating user information. Please check the form.')
        else:
            form = CustomUserForm(instance=custom_user)  # Pass the user instance to prepopulate the form fields
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home_page/')

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
            form.save()
            # Redirect to a success URL or render a success message
            return redirect('home')
        else:
            print("Form is invalid:", form.errors)  # Print form errors for debugging
    else:
        form = AssetBookingForm()
    return render(request, 'new_booking.html', {'form': form})

@login_required
def delete_booking(request, booking_id):
    # Get the booking object or return a 404 error if not found
    booking = get_object_or_404(AssetBooking, booking_id=booking_id)
    
    # Delete instances from Assetbooking where the booking_id is referenced
    AssetBooking.objects.filter(booking_id=booking_id).delete()
    
    # Now delete the user itself
    booking.delete()
    
    return redirect('home')  # Redirect to a page that lists all users after deletion

