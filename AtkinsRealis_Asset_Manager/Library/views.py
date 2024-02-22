from django.http import HttpResponse
from django.contrib import messages
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import CustomUserForm, CustomUserCreationForm
from .models import CustomUser
from django.db import transaction


# Create your views here.

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
        form = AuthenticationForm()
    return render(request, 'login_page.html', {'form': form})

def home(request):
    # create a dictionary 
    myusers = CustomUser.objects.all().values()

    for user in myusers:
        user['password'] = '*' * 12

    context = { 
            "myusers" : myusers, 
        } 
    # return response 
    return render(request, "home.html", context)

def create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                custom_user = form.save()  # Save user in CustomUser model
                # Create corresponding User object
                user = User.objects.create_user(username=custom_user.username, email=custom_user.email, password=form.cleaned_data['password'])
            messages.success(request, 'User created successfully.')
            return redirect('login')  # Redirect to login page on successful submission
        else:
            # Handle form validation errors
            messages.error(request, 'Error creating user. Please check the form.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form})
    
def info(request):
    user = request.user
    print(user)
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
        # Redirect to a specific URL or view function when user is not found
        return redirect('login')

    return render(request, 'user_info.html', {'form': form})