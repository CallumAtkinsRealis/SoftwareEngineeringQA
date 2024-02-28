from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserForm, CustomUserCreationForm, AssetBookingForm
from .models import CustomUser, AssetBooking
from django.db import transaction

# Create your views here.

@login_required
def default(request):
    return redirect('login')

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home_page')  # Redirect to some page after login
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = AuthenticationForm()
    return render(request, 'login_page.html', {'form': form, 'error_messages': messages.get_messages(request)})

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
def create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                custom_user = form.save()  # Save user in CustomUser model
                # Create corresponding User object
                user = User.objects.create_user(username=custom_user.username, email=custom_user.email, password=form.cleaned_data['password'])
                messages.success(request, 'User created successfully.')
                return redirect('home')  # Redirect to login page on successful submission
        else:
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def info(request):
    user = request.user
    try:
        custom_user = CustomUser.objects.get(username=user)
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
        return redirect('login')

    return render(request, 'user_info.html', {'form': form, 'error_messages': messages.get_messages(request)})

@login_required
def assetbooking(request):
    if request.method == 'POST':
        form = AssetBookingForm(request.POST)
        if form.is_valid():
            form.save()
            print("im here")
            # Redirect to a success URL or render a success message
            return redirect('home')
        else:
            print("Form is invalid:", form.errors)  # Print form errors for debugging
    else:
        form = AssetBookingForm()
        print("ive gone wrong")
    return render(request, 'new_booking.html', {'form': form})

