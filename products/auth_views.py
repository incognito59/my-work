from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import re

# 🔐 Email Validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# 🔐 Enhanced Register with Email Validation
@require_http_methods(["GET", "POST"])
def register_enhanced(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Validation
        if not username or len(username) < 3:
            messages.error(request, "❌ Username must be at least 3 characters.")
            return redirect('products:register-enhanced')
        
        if not is_valid_email(email):
            messages.error(request, "❌ Please enter a valid email address.")
            return redirect('products:register-enhanced')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already registered.")
            return redirect('products:register-enhanced')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken.")
            return redirect('products:register-enhanced')
        
        if len(password) < 8:
            messages.error(request, "❌ Password must be at least 8 characters.")
            return redirect('products:register-enhanced')
        
        if password != password_confirm:
            messages.error(request, "❌ Passwords do not match.")
            return redirect('products:register-enhanced')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        messages.success(request, f"✅ Account created! Welcome, {username}. Please log in.")
        return redirect('products:login-enhanced')
    
    return render(request, 'auth/register_enhanced.html')

# 🔐 Enhanced Login
@require_http_methods(["GET", "POST"])
def login_enhanced(request):
    if request.user.is_authenticated:
        return redirect('products:profile')
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '')
        
        user = None
        
        # Try username
        if User.objects.filter(username=username_or_email).exists():
            user = authenticate(request, username=username_or_email, password=password)
        # Try email
        elif User.objects.filter(email=username_or_email).exists():
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(request, username=user_obj.username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"✅ Welcome back, {user.username}!")
            return redirect('products:profile')
        else:
            messages.error(request, "❌ Invalid username/email or password.")
            return redirect('products:login-enhanced')
    
    return render(request, 'auth/login_enhanced.html')

# 🔐 Logout
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.success(request, "✅ You have been logged out.")
    return redirect('products:product-list')

# 👤 User Profile
@login_required(login_url='products:login-enhanced')
def user_profile(request):
    user = request.user
    orders = user.orders.all() if hasattr(user, 'orders') else []
    
    context = {
        'user': user,
        'orders': orders,
        'total_orders': orders.count(),
        'email': user.email,
        'joined_date': user.date_joined,
    }
    return render(request, 'auth/profile.html', context)

# 👤 Update Profile
@login_required(login_url='products:login-enhanced')
@require_http_methods(["GET", "POST"])
def update_profile(request):
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, "✅ Profile updated successfully!")
        return redirect('products:profile')
    
    context = {'user': user}
    return render(request, 'auth/update_profile.html', context)

# 🔑 Password Reset
@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(email=email)
            # In production, send email with reset link
            messages.info(request, f"✅ If {email} exists, a reset link has been sent.")
            return redirect('products:login-enhanced')
        except User.DoesNotExist:
            messages.info(request, f"✅ If {email} exists, a reset link has been sent.")
            return redirect('products:login-enhanced')
    
    return render(request, 'auth/password_reset.html')

# 🌐 Social Login Page
def social_login_page(request):
    if request.user.is_authenticated:
        return redirect('products:profile')
    
    context = {
        'google_client_id': 'YOUR_GOOGLE_CLIENT_ID',  # Add your credentials
        'facebook_app_id': 'YOUR_FACEBOOK_APP_ID',
        'github_client_id': 'YOUR_GITHUB_CLIENT_ID',
    }
    return render(request, 'auth/social_login.html', context)
