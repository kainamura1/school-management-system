from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from django.views.decorators.http import require_http_methods
from student.models import StudentProfile  # Import the StudentProfile model

def home(request):
    return render(request, 'accounts/home.html')

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'student'  # Set default user type to student
            user.save()
            
            # Create a student profile for the user
            StudentProfile.objects.create(
                user=user,
                registration_number=f"STU{user.id}",
                department="Not Specified",
                year_of_study=1
            )
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user type
                if user.user_type == 'student':
                    return redirect('student:dashboard')
                elif user.user_type == 'lecturer':
                    return redirect('lecturer:dashboard')
                elif user.is_staff:
                    return redirect('admin:index')
                else:
                    return redirect('accounts:profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    # Base dashboard that redirects to specific dashboards
    if request.user.user_type == 'student':
        return redirect('student:dashboard')
    elif request.user.user_type == 'lecturer':
        return redirect('lecturer:dashboard')
    else:
        # For admin or undefined user types
        return render(request, 'accounts/dashboard.html')

def about_view(request):
    """View for About Us page"""
    return render(request, 'accounts/about.html')

def contact_view(request):
    """View for Contact page"""
    if request.method == 'POST':
        # In a real application, you'd process the form data here
        # For example, send an email or save to database
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Show success message
        messages.success(request, "Your message has been sent! We'll get back to you soon.")
        return redirect('accounts:contact')
        
    return render(request, 'accounts/contact.html')
