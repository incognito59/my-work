from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product, Comment, Order, Offer
from django.conf import settings

try:
    import stripe
    stripe_api_available = True
except Exception:
    stripe_api_available = False


# 🏠 Home / Search Page
def index(request):
    """Shop page with products organized by category"""
    query = request.GET.get('q') or request.GET.get('search')

    # Build categories dynamically from actual product data
    category_values = Product.objects.order_by('category').values_list('category', flat=True).distinct()

    products_by_category = {}
    available_categories = []
    for category_code in category_values:
        category_label = category_code or 'Uncategorized'

        if query:
            products = Product.objects.filter(
                category=category_code,
                name__icontains=query
            )
        else:
            products = Product.objects.filter(category=category_code)

        if products.exists():
            products_by_category[category_code or 'Uncategorized'] = {
                'label': category_label,
                'products': products
            }
            available_categories.append((category_code or 'Uncategorized', category_label))

    available_categories.sort(key=lambda item: item[1])

    latest_products = Product.objects.order_by('-id')[:8]
    best_deals = Offer.objects.all()[:4]

    return render(request, 'index.html', {
        'products_by_category': products_by_category,
        'query': query,
        'available_categories': available_categories,
        'latest_products': latest_products,
        'best_deals': best_deals,
    })


# 🎯 Landing Page with Registration
def landing_page(request):
    """Landing page with featured products, offers, and registration"""
    # Get featured products (newest first)
    featured_products = Product.objects.all().order_by('-id')[:6]
    
    # Get active offers
    offers = Offer.objects.all()[:4]
    
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Validation
        if not username or len(username) < 3:
            messages.error(request, "❌ Username must be at least 3 characters.")
            return render(request, 'landing.html')

        if not email:
            messages.error(request, "❌ Email is required.")
            return render(request, 'landing.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "❌ Email already registered.")
            return render(request, 'landing.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken.")
            return render(request, 'landing.html')

        if len(password) < 8:
            messages.error(request, "❌ Password must be at least 8 characters.")
            return render(request, 'landing.html')

        if password != password_confirm:
            messages.error(request, "❌ Passwords do not match.")
            return render(request, 'landing.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # Send welcome email
        try:
            from .utils import send_welcome_email
            send_welcome_email(user)
        except Exception as e:
            print(f"Email error: {e}")
        
        messages.success(request, f"✅ Account created! Welcome, {username}. Please log in.")
        return redirect('products:login')
    
    return render(request, 'landing.html', {
        'featured_products': featured_products,
        'offers': offers,
    })


def offers_page(request):
    """Display active offers and sample products with discounted prices"""
    offers = Offer.objects.all()
    products = Product.objects.all().order_by('-id')  # newest first

    return render(request, 'offers.html', {
        'offers': offers,
        'products': products,
    })

# Login Page
def login_page(request):
    # DEPRECATED: Use login_enhanced instead
    return login_enhanced(request)


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


from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView
from django.urls import reverse_lazy


#  Password Reset Page
class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('products:password-reset-done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    from_email = 'afolabiprosper329@gmail.com'


# 📧 Password Reset Done Page (Check Email)
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


# 🔐 Password Reset Confirm Page
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('products:login')
    post_reset_login = True


# �📝 Register Page
def register_page(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        full_name = f"{first_name} {last_name}".strip()
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password') or request.POST.get('password1')
        password2 = request.POST.get('password_confirm')

        # Derive a username from email or full_name
        username = request.POST.get('username', '').strip()

        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'register.html')
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
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, "Account created! Please log in.")
        return redirect('products:login')
    
    return render(request, 'register.html')


# � Enhanced Register Page
def register_enhanced(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Validation
        if not username or len(username) < 3:
            messages.error(request, "❌ Username must be at least 3 characters.")
            return render(request, 'auth/register_enhanced.html')

        if not email:
            messages.error(request, "❌ Email is required.")
            return render(request, 'auth/register_enhanced.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "❌ Email already registered.")
            return render(request, 'auth/register_enhanced.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken.")
            return render(request, 'auth/register_enhanced.html')

        if len(password) < 8:
            messages.error(request, "❌ Password must be at least 8 characters.")
            return render(request, 'auth/register_enhanced.html')

        if password != password_confirm:
            messages.error(request, "❌ Passwords do not match.")
            return render(request, 'auth/register_enhanced.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        messages.success(request, f"✅ Account created! Welcome, {username}. Please log in.")
        return redirect('products:login')
    
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


# ============ NEW FEATURES (Phase 1-3) ============

# 📧 Contact Form
def contact_us(request):
    from .models import ContactFormSubmission
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if all([name, email, subject, message]):
            ContactFormSubmission.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            messages.success(request, "✅ Thank you! We've received your message. We'll respond within 24 hours.")
            return redirect('products:contact')
        else:
            messages.error(request, "❌ Please fill in all fields.")
    
    return render(request, 'contact.html')


# ❓ FAQ Page
def faq(request):
    from .models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    categories = set(faq.category for faq in faqs)
    
    category = request.GET.get('category')
    if category:
        faqs = faqs.filter(category=category)
    
    return render(request, 'faq.html', {
        'faqs': faqs,
        'categories': categories,
        'selected_category': category,
    })


# 🎫 Support Tickets (User)
@login_required(login_url='products:login')
def my_tickets(request):
    from .models import SupportTicket
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'support/my_tickets.html', {
        'tickets': tickets,
    })


@login_required(login_url='products:login')
def create_ticket(request):
    from .models import SupportTicket
    from .utils import track_product_view
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        order_id = request.POST.get('order_id')
        
        if title and description:
            order = None
            if order_id:
                try:
                    order = Order.objects.get(id=order_id, user=request.user)
                except Order.DoesNotExist:
                    pass
            
            ticket = SupportTicket.objects.create(
                user=request.user,
                order=order,
                title=title,
                description=description,
                priority=priority
            )
            messages.success(request, f"✅ Support ticket #{ticket.id} created successfully!")
            return redirect('products:ticket-detail', ticket_id=ticket.id)
        else:
            messages.error(request, "❌ Please fill in all required fields.")
    
    orders = Order.objects.filter(user=request.user)
    return render(request, 'support/create_ticket.html', {
        'orders': orders,
    })


@login_required(login_url='products:login')
def ticket_detail(request, ticket_id):
    from .models import SupportTicket, TicketReply
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Check if user is the ticket owner or admin
    if not (request.user == ticket.user or request.user.is_staff):
        messages.error(request, "❌ You don't have permission to view this ticket.")
        return redirect('products:my-tickets')
    
    replies = ticket.replies.all().order_by('created_at')
    
    if request.method == 'POST' and request.user == ticket.user:
        message = request.POST.get('message', '').strip()
        if message:
            TicketReply.objects.create(
                ticket=ticket,
                message=message,
                is_admin_reply=False
            )
            messages.success(request, "✅ Your reply has been added.")
            return redirect('products:ticket-detail', ticket_id=ticket.id)
    
    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'replies': replies,
    })


# 📱 Shipping Addresses
@login_required(login_url='products:login')
def addresses(request):
    from .models import UserAddress
    addresses = UserAddress.objects.filter(user=request.user)
    
    return render(request, 'account/addresses.html', {
        'addresses': addresses,
    })


@login_required(login_url='products:login')
def add_address(request):
    from .models import UserAddress
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        street_address = request.POST.get('street_address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        address_type = request.POST.get('address_type', 'home')
        is_default = request.POST.get('is_default') == 'on'
        
        if all([full_name, phone, street_address, city, state, postal_code]):
            UserAddress.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                street_address=street_address,
                city=city,
                state=state,
                postal_code=postal_code,
                address_type=address_type,
                is_default=is_default
            )
            messages.success(request, "✅ Address added successfully!")
            return redirect('products:addresses')
        else:
            messages.error(request, "❌ Please fill in all required fields.")
    
    return render(request, 'account/add_address.html')


# 💳 Payment Methods
@login_required(login_url='products:login')
def payment_methods(request):
    from .models import PaymentMethod
    methods = PaymentMethod.objects.filter(user=request.user)
    
    return render(request, 'account/payment_methods.html', {
        'methods': methods,
    })


# 📊 Dashboard/Analytics
def analytics_dashboard(request):
    """Admin analytics dashboard"""
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('products:product-list')
    
    from .models import Order, Product, ProductView
    from django.db.models import Count, Sum
    
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
    total_products = Product.objects.count()
    total_views = ProductView.objects.count()
    
    # Trending products
    trending = ProductView.objects.values('product__name').annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:5]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_views': total_views,
        'trending_products': trending,
    }
    
    return render(request, 'admin/dashboard.html', context)


# 🏷️ Newsletter Signup
def newsletter_signup(request):
    if request.method == 'POST':
        from .models import Newsletter
        email = request.POST.get('email', '').strip()
        
        if email:
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            if created:
                messages.success(request, "✅ Successfully subscribed to our newsletter!")
            else:
                messages.info(request, "📧 You're already subscribed!")
            return redirect('products:product-list')
    
    messages.error(request, "❌ Please provide a valid email address.")
    return redirect('products:product-list')


# 🏷️ Offers & Discounts Page
def offers_page(request):
    """Display all offers with discounted products"""
    from .models import Offer
    
    # Get all active offers
    offers = Offer.objects.all()
    
    # Get products by category
    categories = Product.CATEGORY_CHOICES
    products_by_category = {}
    
    for category_code, category_name in categories:
        products_by_category[category_name] = Product.objects.filter(category=category_code)[:6]
    
    context = {
        'offers': offers,
        'products_by_category': products_by_category,
        'categories': categories,
    }
    
    return render(request, 'offers.html', context)


# ============ EMAIL TEMPLATE PREVIEW (Development/Testing) ============

def preview_email_welcome(request):
    """Preview welcome email template"""
    context = {
        'site_name': 'RedCart',
        'username': 'John Doe',
    }
    return render(request, 'emails/welcome.html', context)


def preview_email_order_confirmation(request):
    """Preview order confirmation email template"""
    from django.utils import timezone
    
    # Create sample context
    sample_order = type('Order', (), {
        'id': 12345,
        'created_at': timezone.now(),
        'get_status_display': 'Pending',
        'total': 150.00,
    })()
    
    sample_item = type('OrderItem', (), {
        'product': type('Product', (), {'name': 'Sample Product'}),
        'quantity': 2,
        'price': 75.00,
        'total_price': 150.00,
    })()
    
    context = {
        'order': sample_order,
        'items': [sample_item],
        'site_name': 'RedCart',
        'user': type('User', (), {
            'first_name': 'John',
            'username': 'johndoe'
        }),
    }
    return render(request, 'emails/order_confirmation.html', context)


def preview_email_order_shipped(request):
    """Preview order shipped email template"""
    from django.utils import timezone
    
    context = {
        'order': type('Order', (), {
            'id': 12345,
            'shipped_date': timezone.now(),
            'tracking_number': 'TRK123456789',
        }),
        'site_name': 'RedCart',
        'user': type('User', (), {
            'first_name': 'John',
            'username': 'johndoe'
        }),
    }
    return render(request, 'emails/order_shipped.html', context)


def preview_email_order_delivered(request):
    """Preview order delivered email template"""
    from django.utils import timezone
    
    context = {
        'order': type('Order', (), {
            'id': 12345,
            'delivered_date': timezone.now(),
        }),
        'site_name': 'RedCart',
        'user': type('User', (), {
            'first_name': 'John',
            'username': 'johndoe'
        }),
    }
    return render(request, 'emails/order_delivered.html', context)


def preview_email_contact_reply(request):
    """Preview contact form reply email template"""
    context = {
        'name': 'John Doe',
        'subject': 'Question about shipping costs',
        'reply': 'Thank you for contacting us. We appreciate your inquiry. Our standard shipping costs are based on weight and destination...',
        'site_name': 'RedCart',
    }
    return render(request, 'emails/contact_reply.html', context)


def preview_email_password_reset(request):
    """Preview password reset email template"""
    context = {
        'site_name': 'RedCart',
        'user': type('User', (), {
            'first_name': 'John',
            'username': 'johndoe'
        }),
        'reset_link': 'http://127.0.0.1:8000/products/password-reset/',
    }
    return render(request, 'emails/password_reset.html', context)


# ============ NEW PAGES ============

# 📝 Blog / Articles Page
def blog_page(request):
    """Blog page with articles about products and shopping tips"""
    # Sample blog articles data (in production, would come from a Blog model)
    articles = [
        {
            'id': 1,
            'title': 'Top 10 Shopping Tips for Smart Buyers',
            'excerpt': 'Learn how to shop smarter and save more with these proven strategies...',
            'date': '2024-04-15',
            'author': 'Sarah Johnson',
            'category': 'Shopping Tips',
            'image_emoji': '💡',
            'slug': 'top-10-shopping-tips'
        },
        {
            'id': 2,
            'title': 'How to Choose the Right Product',
            'excerpt': 'A comprehensive guide to selecting products that match your needs and budget...',
            'date': '2024-04-10',
            'author': 'Michael Smith',
            'category': 'Buying Guide',
            'image_emoji': '🛍️',
            'slug': 'how-to-choose-product'
        },
        {
            'id': 3,
            'title': 'The Benefits of Free Shipping',
            'excerpt': 'Discover why free shipping saves you money and improves your shopping experience...',
            'date': '2024-04-05',
            'author': 'Emma Wilson',
            'category': 'Promotions',
            'image_emoji': '🚚',
            'slug': 'benefits-free-shipping'
        },
        {
            'id': 4,
            'title': 'Seasonal Sales Guide',
            'excerpt': 'Plan your purchases around our biggest sales events of the year...',
            'date': '2024-03-28',
            'author': 'Alex Brown',
            'category': 'Deals',
            'image_emoji': '🎉',
            'slug': 'seasonal-sales-guide'
        },
    ]
    
    return render(request, 'blog.html', {
        'articles': articles,
        'total_articles': len(articles),
    })


# ⭐ Product Reviews Showcase Page
def reviews_page(request):
    """Page showcasing customer reviews and ratings"""
    # Get products with reviews
    products_with_reviews = Product.objects.filter(
        comment__isnull=False
    ).distinct()[:8]
    
    # Get all reviews/comments
    all_comments = Comment.objects.all().order_by('-created_at')[:20]
    
    # Summary stats
    total_reviews = Comment.objects.count()
    avg_rating = 4.5  # Would calculate from actual data in production
    
    return render(request, 'reviews.html', {
        'products_with_reviews': products_with_reviews,
        'recent_reviews': all_comments,
        'total_reviews': total_reviews,
        'average_rating': avg_rating,
    })


# 💖 Wishlist / Favorites Page
@login_required(login_url='products:login')
def wishlist_page(request):
    """User's wishlist/favorites page"""
    # Get user's wishlist items
    from .models import Wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
        'total_wishlist': wishlist_items.count(),
        'message': 'Your wishlist is empty. Start adding products!' if not wishlist_items else None,
    }
    return render(request, 'wishlist.html', context)


# ℹ️ About & Store Info Page
def about_page(request):
    """About RedCart and store information page"""
    company_info = {
        'name': 'RedCart',
        'tagline': 'Shop Smart, Live Better',
        'description': 'Your trusted online marketplace for quality products at unbeatable prices.',
        'founded': '2020',
        'email': 'afolabiprosper329@gmail.com',
        'phone': '+234 (0) 801 234 5678',
        'locations': [
            {'city': 'Lagos', 'address': '123 Commercial Avenue, Victoria Island'},
            {'city': 'Abuja', 'address': '45 Business Park, Central Business District'},
        ]
    }
    
    stats = {
        'products': Product.objects.count(),
        'users': User.objects.count(),
        'orders': Order.objects.count(),
        'countries': 1,
    }
    
    team_members = [
        {
            'name': 'John Afolabi',
            'role': 'Founder & CEO',
            'bio': 'Visionary leader with 15+ years in e-commerce',
            'emoji': '👨‍💼'
        },
        {
            'name': 'Sarah Johnson',
            'role': 'Head of Operations',
            'bio': 'Ensuring smooth operations and customer satisfaction',
            'emoji': '👩‍💼'
        },
        {
            'name': 'Michael Smith',
            'role': 'Lead Developer',
            'bio': 'Building the technology that powers RedCart',
            'emoji': '👨‍💻'
        },
        {
            'name': 'Emma Wilson',
            'role': 'Customer Success',
            'bio': 'Making sure every customer gets the best experience',
            'emoji': '👩‍💼'
        },
    ]
    
    return render(request, 'about.html', {
        'company': company_info,
        'stats': stats,
        'team': team_members,
    })
