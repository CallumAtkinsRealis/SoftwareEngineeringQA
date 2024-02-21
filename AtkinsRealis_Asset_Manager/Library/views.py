from django.http import HttpResponse
from django.contrib import messages
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


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
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('create') 
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('create')  
        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'User created successfully.')
        return redirect('login')  # Redirect to login page on sucessful submission
    else:
        return render(request, 'create_user.html')  