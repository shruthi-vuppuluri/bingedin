from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Django's User model uses username, but we're using email for login
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid password')
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist')
            
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists')
            return redirect('signup')
            
        # Create the user
        username = email.split('@')[0]  # Generate username from email
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create the user profile
        UserProfile.objects.create(user=user)
        
        # Log the user in
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
            
    return render(request, 'accounts/signup.html')
