from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm
from .models import CustomUser

def register_view(request):
    """
    Handle user registration with user type selection modal.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        # Get the user_type from the form
        user_type = request.POST.get('user_type')
        
        if form.is_valid():
            # Create user but don't save to database yet
            user = form.save(commit=False)
            
            # Set the user_type
            user.user_type = user_type
            
            # Save the user
            user.save()
            
            # Automatically log in the user after registration
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.success(request, f'Welcome, {user.first_name}! Your {user_type} account has been created.')
            return redirect('home')
        else:
            # If form is not valid, display errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'account/register.html', {'form': form})

def login_view(request):
    """
    Handle user login with improved error handling.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                

                
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'account/login.html', {'form': form})

def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def profile_view(request):
    """
    Display and update user profile.
    """
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'account/profile.html', {'form': form})

def password_reset_request(request):
    """
    Placeholder for future password reset implementation.
    Currently just renders a message.
    """
    messages.info(request, 'Password reset functionality is currently unavailable.')
    return redirect('login')