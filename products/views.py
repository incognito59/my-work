from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product, Comment, Order
from django.conf import settings

try:
    import stripe
    stripe_api_available = True
except Exception:
    stripe_api_available = False


# 🏠 Home / Search Page
def index(request):
    query = request.GET.get('q') or request.GET.get('search')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    categories = []  # Optional: fetch from Category model
    hot_deals = Product.objects.all()[:6]  # Show top 6 as hot deals
    return render(request, 'index.html', {
        'products': products, 
        'query': query,
        'categories': categories,
        'hot_deals': hot_deals
    })


# 🔑 Login Page
def login_page(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        # Accept either email or username from the login form
        email = request.POST.get('email') or request.POST.get('username') or request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = None
        if email and password:
            # Try to find a user by email first
            try:
                user_obj = User.objects.filter(email__iexact=email).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
                else:
                    # Fall back to authenticating with given email as username
                    user = authenticate(request, username=email, password=password)
            except Exception:
                user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}! 🎉")
            return redirect('products:product-list')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    
    return render(request, 'login.html')


# � Enhanced Login Page
def login_enhanced(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password', '').strip()

        user = None
        
        if not username_or_email or not password:
            messages.error(request, "Both email/username and password are required.")
            return render(request, 'auth/login_enhanced.html')

        try:
            # Try to find user by email first (case-insensitive)
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            
            if user_obj:
                # Found by email, authenticate with username
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                # Not found by email, try as username
                user = authenticate(request, username=username_or_email, password=password)
                
        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
            return render(request, 'auth/login_enhanced.html')

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'products:product-list'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email/username or password.")
    
    return render(request, 'auth/login_enhanced.html')


from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy


#  Password Reset Page
class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('products:login')
    email_template_name = 'registration/password_reset_email.html'


# �📝 Register Page
def register_page(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name') or request.POST.get('first_name', '')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password') or request.POST.get('password1')
        password2 = request.POST.get('confirm_password') or request.POST.get('password2')

        # Derive a username from email or full_name
        if email:
            username = email.split('@')[0]
        else:
            username = (full_name or 'user').replace(' ', '_')
        # ensure username uniqueness
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Validation
        if not all([username, email, password1, password2]):
            messages.error(request, "All required fields must be filled.")
            return render(request, 'register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        # set name and optional phone
        if full_name:
            user.first_name = full_name
        user.save()
        messages.success(request, "Account created! Please log in.")
        return redirect('products:login')
    
    return render(request, 'register.html')


# � Enhanced Register Page
def register_enhanced(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Derive a username from email
        if email:
            username = email.split('@')[0]
        else:
            username = (full_name or 'user').replace(' ', '_')
        
        # Ensure username uniqueness
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Validation
        if not all([email, password1, password2]):
            messages.error(request, "All required fields must be filled.")
            return render(request, 'auth/register_enhanced.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/register_enhanced.html')

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return render(request, 'auth/register_enhanced.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'auth/register_enhanced.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        # set name
        if full_name:
            user.first_name = full_name
        user.save()
        messages.success(request, "Account created! Please log in.")
        return redirect('products:login-enhanced')
    
    return render(request, 'auth/register_enhanced.html')


# �🚪 Logout
def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('products:product-list')


# 👤 User Profile Page
@login_required(login_url='products:login')
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders,
        'order_count': orders.count(),
    }
    
    return render(request, 'profile.html', context)


# ➕ Add to Cart (Success Message)
def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    cart = request.session.get('cart', {})

    product_id = str(product.id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    cart_url = reverse('products:view-cart')
    messages.success(
        request,
        f"🛒 {product.name} added to your cart! "
        f"<a href='{cart_url}' class='btn btn-sm btn-outline-light ms-2'>Check Cart Now</a>",
        extra_tags='safe'
    )
    return redirect('products:product-list')


# 🛒 View Cart Page
def view_cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.quantity = quantity
        product.total_price = product.price * quantity
        products.append(product)
        total += product.total_price

    context = {
        'products': products,
        'total': total,
        'query': request.GET.get('q', ''),
    }
    return render(request, 'cart.html', context)


# ❌ Delete Item from Cart
def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.info(request, "🗑️ Item removed from your cart successfully.")
    else:
        messages.warning(request, "Item not found in your cart.")

    return redirect('products:view-cart')


# 💳 Checkout Page
def checkout(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.quantity = quantity
        product.total_price = product.price * quantity
        products.append(product)
        total += product.total_price

    total_kobo = int(total * 100)

    context = {
        'products': products,
        'total': total,
        'total_kobo': total_kobo,
        'query': request.GET.get('q', ''),
    }

    # If Stripe keys are configured, create a test PaymentIntent and provide client secret
    if stripe_api_available and settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            intent = stripe.PaymentIntent.create(
                amount=total_kobo or 0,
                currency='usd',
                automatic_payment_methods={'enabled': True},
            )
            context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
            context['stripe_client_secret'] = intent.client_secret
        except Exception:
            # fall back quietly to manual payment if stripe call fails
            pass
    else:
        # expose publishable key if set (even if stripe package not installed)
        if getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''):
            context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
    return render(request, 'checkout.html', context)


# ✅ Confirm Payment
def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "✅ Payment confirmed! Thank you for shopping with RedCart.")
        request.session['cart'] = {}
        return redirect('products:product-list')
    return redirect('products:checkout')


# 📦 Product Detail Page + Comments
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    additional_images = getattr(product, 'additional_images', [])
    comments = product.comments.all().order_by('-created_at') if hasattr(product, 'comments') else []

    if request.method == 'POST':
        name = request.POST.get('name')
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        if name and text and rating:
            Comment.objects.create(product=product, name=name, text=text, rating=rating)
            messages.success(request, "💬 Thank you for your review!")
            return redirect('products:product-detail', product_id=product.id)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'additional_images': additional_images,
        'query': request.GET.get('q', ''),
    })


# ⚡ Buy Now (Direct Checkout)
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['cart'] = {str(product.id): 1}
    return redirect('products:checkout')
