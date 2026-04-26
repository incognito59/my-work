from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Comment, Order, Offer, Wishlist, Coupon, AbandonedCart
from .utils import get_product_recommendations_ai, get_ai_chat_response
from django.conf import settings


def _get_coupon_context(request, subtotal):
    coupon_code = request.session.get('coupon_code', '')
    coupon = None
    discount = 0
    message = ''

    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if coupon and coupon.is_valid(subtotal):
            discount = coupon.calculate_discount(subtotal)
            message = f"Coupon '{coupon.code}' applied."
        else:
            discount = 0
            request.session.pop('coupon_code', None)
            if coupon:
                if coupon.expiry_date <= timezone.now():
                    message = 'This coupon has expired.'
                elif subtotal < coupon.min_order_amount:
                    message = f'Minimum order of ₦{coupon.min_order_amount:,.2f} required.'
                else:
                    message = 'This coupon is not valid for your order.'
            else:
                message = 'Coupon code not found.'

    return {
        'coupon_code': coupon_code,
        'coupon_discount': discount,
        'coupon_message': message,
        'coupon': coupon,
    }


def _sync_abandoned_cart(request, cart):
    if not request.user.is_authenticated:
        return

    if cart:
        AbandonedCart.objects.update_or_create(
            user=request.user,
            defaults={
                'cart_data': cart,
                'active': True,
            }
        )
    else:
        AbandonedCart.objects.filter(user=request.user, active=True).update(active=False)

try:
    import stripe
    stripe_api_available = True
except Exception:
    stripe_api_available = False


# 🏠 Home / Search Page
def index(request):
    """Shop page with products organized by category"""
    query = request.GET.get('q') or request.GET.get('search')

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

    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'index.html', {
        'products_by_category': products_by_category,
        'query': query,
        'available_categories': available_categories,
        'latest_products': latest_products,
        'best_deals': best_deals,
        'wishlisted_ids': wishlisted_ids,
    })


# 🎯 Landing Page with Registration
def landing_page(request):
    """Landing page with featured products, offers, and registration"""
    featured_products = Product.objects.all().order_by('-id')[:6]
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
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
    products = Product.objects.all().order_by('-id')

    return render(request, 'offers.html', {
        'offers': offers,
        'products': products,
    })


# Login Page
def login_page(request):
    return login_enhanced(request)


# 🔐 Enhanced Login Page
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
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
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


# Password Reset Page
class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('products:password-reset-done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    from_email = 'afolabiprosper329@gmail.com'


# 📧 Password Reset Done Page
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


# 🔐 Password Reset Confirm Page
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('products:login')
    post_reset_login = True


# 📝 Register Page
def register_page(request):
    if request.user.is_authenticated:
        return redirect('products:product-list')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email')
        password1 = request.POST.get('password') or request.POST.get('password1')
        password2 = request.POST.get('password_confirm')

        username = request.POST.get('username', '').strip()

        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'register.html')

        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, "Account created! Please log in.")
        return redirect('products:login')
    
    return render(request, 'register.html')


# 📝 Enhanced Register Page
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


# 🚪 Logout
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


# ➕ Add to Cart
def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    if product.is_out_of_stock:
        messages.error(request, f"⚠️ {product.name} is out of stock and cannot be added to the cart.")
        return redirect('products:product-detail', product_id=product.id)

    cart = request.session.get('cart', {})
    product_id = str(product.id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    _sync_abandoned_cart(request, cart)

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

    coupon_context = _get_coupon_context(request, total)
    coupon_discount = coupon_context['coupon_discount']
    total_after_coupon = max(0, total - coupon_discount)

    context = {
        'products': products,
        'total': total,
        'total_after_coupon': total_after_coupon,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_context['coupon_code'],
        'coupon_message': coupon_context['coupon_message'],
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
        _sync_abandoned_cart(request, cart)
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

    coupon_context = _get_coupon_context(request, total)
    coupon_discount = coupon_context['coupon_discount']
    total_after_coupon = max(0, total - coupon_discount)

    context = {
        'products': products,
        'total': total,
        'total_after_coupon': total_after_coupon,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_context['coupon_code'],
        'coupon_message': coupon_context['coupon_message'],
        'total_kobo': total_kobo,
        'query': request.GET.get('q', ''),
    }

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
            pass
    else:
        if getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''):
            context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY

    return render(request, 'checkout.html', context)


# ✅ Confirm Payment
def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "✅ Payment confirmed! Thank you for shopping with RedCart.")
        request.session['cart'] = {}
        request.session.pop('coupon_code', None)
        _sync_abandoned_cart(request, {})
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

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    # ✅ Updated to use new function name
    ai_recommendations = get_product_recommendations_ai(product, limit=4)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'additional_images': additional_images,
        'query': request.GET.get('q', ''),
        'is_in_wishlist': is_in_wishlist,
        'ai_recommendations': ai_recommendations,
    })


# ⚡ Buy Now
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.is_out_of_stock:
        messages.error(request, f"⚠️ {product.name} is out of stock.")
        return redirect('products:product-detail', product_id=product.id)

    cart = {str(product.id): 1}
    request.session['cart'] = cart
    _sync_abandoned_cart(request, cart)
    return redirect('products:checkout')


# ============ NEW FEATURES ============

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


# 🎫 Support Tickets
@login_required(login_url='products:login')
def my_tickets(request):
    from .models import SupportTicket
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/my_tickets.html', {'tickets': tickets})


@login_required(login_url='products:login')
def create_ticket(request):
    from .models import SupportTicket
    
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
    return render(request, 'support/create_ticket.html', {'orders': orders})


@login_required(login_url='products:login')
def ticket_detail(request, ticket_id):
    from .models import SupportTicket, TicketReply
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
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
    return render(request, 'account/addresses.html', {'addresses': addresses})


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
    return render(request, 'account/payment_methods.html', {'methods': methods})


# 📊 Analytics Dashboard
def analytics_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('products:product-list')
    
    from .models import Order, Product, ProductView
    from django.db.models import Count, Sum
    
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(is_paid=True).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
    total_products = Product.objects.count()
    total_views = ProductView.objects.count()
    
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


# ============ EMAIL TEMPLATE PREVIEWS ============

def preview_email_welcome(request):
    context = {'site_name': 'RedCart', 'username': 'John Doe'}
    return render(request, 'emails/welcome.html', context)


def preview_email_order_confirmation(request):
    from django.utils import timezone
    
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
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    }
    return render(request, 'emails/order_confirmation.html', context)


def preview_email_order_shipped(request):
    from django.utils import timezone
    context = {
        'order': type('Order', (), {
            'id': 12345,
            'shipped_date': timezone.now(),
            'tracking_number': 'TRK123456789',
        }),
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    }
    return render(request, 'emails/order_shipped.html', context)


def preview_email_order_delivered(request):
    from django.utils import timezone
    context = {
        'order': type('Order', (), {
            'id': 12345,
            'delivered_date': timezone.now(),
        }),
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    }
    return render(request, 'emails/order_delivered.html', context)


def preview_email_contact_reply(request):
    context = {
        'name': 'John Doe',
        'subject': 'Question about shipping costs',
        'reply': 'Thank you for contacting us...',
        'site_name': 'RedCart',
    }
    return render(request, 'emails/contact_reply.html', context)


def preview_email_password_reset(request):
    context = {
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
        'reset_link': 'http://127.0.0.1:8000/products/password-reset/',
    }
    return render(request, 'emails/password_reset.html', context)


# ============ NEW PAGES ============

# 📝 Blog Page
def blog_page(request):
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


# ⭐ Reviews Page
def reviews_page(request):
    products_with_reviews = Product.objects.filter(
        comment__isnull=False
    ).distinct()[:8]
    
    all_comments = Comment.objects.all().order_by('-created_at')[:20]
    total_reviews = Comment.objects.count()
    
    return render(request, 'reviews.html', {
        'products_with_reviews': products_with_reviews,
        'recent_reviews': all_comments,
        'total_reviews': total_reviews,
        'average_rating': 4.5,
    })


# 💖 Wishlist Toggle
def toggle_wishlist(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    if not request.user.is_authenticated:
        login_url = reverse('products:login') + '?next=' + reverse('products:wishlist')
        return JsonResponse({'success': False, 'login_url': login_url}, status=401)

    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        action = 'removed'
    else:
        action = 'added'

    return JsonResponse({'success': True, 'action': action, 'product_id': product_id})


# 🤖 AI Chat Endpoint
def ai_chat(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        payload = {}

    message = payload.get('message') or request.POST.get('message')
    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required.'}, status=400)

    reply = get_ai_chat_response(message)
    return JsonResponse({'success': True, 'reply': reply})


def apply_coupon(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        payload = {}

    code = (payload.get('code') or '').strip()
    if not code:
        return JsonResponse({'success': False, 'error': 'Coupon code required.'}, status=400)

    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'success': False, 'error': 'Your cart is empty.'}, status=400)

    subtotal = 0
    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if product:
            subtotal += product.price * quantity

    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return JsonResponse({'success': False, 'error': 'Coupon not found.'}, status=404)

    if coupon.expiry_date <= timezone.now() or not coupon.is_active:
        return JsonResponse({'success': False, 'error': 'This coupon is not active or has expired.'}, status=400)

    if subtotal < coupon.min_order_amount:
        return JsonResponse({
            'success': False,
            'error': f'Minimum order amount is ₦{coupon.min_order_amount:,.2f}.',
        }, status=400)

    discount = coupon.calculate_discount(subtotal)
    request.session['coupon_code'] = coupon.code

    return JsonResponse({
        'success': True,
        'discount': discount,
        'coupon_code': coupon.code,
        'message': f"Coupon '{coupon.code}' applied successfully.",
    })


def recently_viewed(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        payload = {}

    ids = payload.get('ids', [])
    if not isinstance(ids, list):
        return JsonResponse({'success': False, 'error': 'Invalid ids list.'}, status=400)

    products = []
    seen = set()
    for raw_id in ids:
        try:
            product_id = int(raw_id)
        except (ValueError, TypeError):
            continue
        if product_id in seen:
            continue
        seen.add(product_id)
        product = Product.objects.filter(id=product_id).first()
        if product:
            products.append({
                'id': product.id,
                'name': product.name,
                'image_src': product.image_src,
                'price': f"{product.price:.2f}",
                'is_out_of_stock': product.is_out_of_stock,
            })
        if len(products) >= 6:
            break

    return JsonResponse({'success': True, 'recently_viewed': products})


# 💖 Wishlist Page
def wishlist_page(request):
    wishlist_items = []
    message = None

    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        if not wishlist_items:
            message = 'Your wishlist is empty. Start adding products!'
    else:
        message = 'Log in to view and save your wishlist items.'

    context = {
        'wishlist_items': wishlist_items,
        'total_wishlist': wishlist_items.count() if request.user.is_authenticated else 0,
        'message': message,
    }
    return render(request, 'wishlist.html', context)


# ℹ️ About Page
def about_page(request):
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
        {'name': 'John Afolabi', 'role': 'Founder & CEO', 'bio': 'Visionary leader with 15+ years in e-commerce', 'emoji': '👨‍💼'},
        {'name': 'Sarah Johnson', 'role': 'Head of Operations', 'bio': 'Ensuring smooth operations and customer satisfaction', 'emoji': '👩‍💼'},
        {'name': 'Michael Smith', 'role': 'Lead Developer', 'bio': 'Building the technology that powers RedCart', 'emoji': '👨‍💻'},
        {'name': 'Emma Wilson', 'role': 'Customer Success', 'bio': 'Making sure every customer gets the best experience', 'emoji': '👩‍💼'},
    ]
    
    return render(request, 'about.html', {
        'company': company_info,
        'stats': stats,
        'team': team_members,
    })