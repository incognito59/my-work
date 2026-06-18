from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import json
import traceback
import urllib.request
import urllib.error

from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .models import Product, Comment, Order, OrderItem, Wishlist, AbandonedCart, Coupon
from .utils import get_product_recommendations_ai, get_ai_chat_response, update_stock
from django.conf import settings

from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Notification, UserNotificationSettings, PushNotificationSubscription, SystemAlert, NotificationLog
from django.core.cache import cache


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


# ============ FIREBASE AUTH ============

@csrf_exempt
def firebase_auth_callback(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)

    id_token = payload.get('token')
    if not id_token:
        return JsonResponse({'success': False, 'error': 'Token required.'}, status=400)

    try:
        verify_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
        with urllib.request.urlopen(verify_url) as response:
            token_data = json.loads(response.read().decode())

        expected_audience = '774139839237-3e62lmii9cvo2ju690b5hsb79cksol4e.apps.googleusercontent.com'
        if token_data.get('aud') != expected_audience:
            return JsonResponse({'success': False, 'error': 'Invalid token audience.'}, status=401)

        email = token_data.get('email')
        name = token_data.get('name', '')
        if not email:
            return JsonResponse({'success': False, 'error': 'No email in token.'}, status=400)

        user = User.objects.filter(email__iexact=email).first()
        created = False

        if not user:
            created = True
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(username=username, email=email, password=None)

        if name and not user.first_name:
            parts = name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        messages.success(request, f"✅ Welcome back, {user.first_name or user.username}!")

        return JsonResponse({'success': True, 'created': created, 'email': email, 'redirect': '/products/'})

    except urllib.error.URLError:
        return JsonResponse({'success': False, 'error': 'Token verification failed.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============ PAYSTACK PAYMENT VERIFY ============

def paystack_verify(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, '❌ No payment reference found.')
        return redirect('products:checkout')

    try:
        import requests
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
        result = response.json()

        if result.get('status') and result.get('data', {}).get('status') == 'success':
            amount = result['data']['amount'] / 100

            if request.user.is_authenticated:
                cart = request.session.get('cart', {})

                order = Order.objects.create(
                    user=request.user,
                    subtotal=amount,
                    discount=0,
                    is_paid=True,
                    payment_status='paid',
                    status='confirmed'
                )

                for product_id, item_data in cart.items():
                    try:
                        product = Product.objects.get(id=int(product_id))
                        quantity = int(item_data.get('quantity', 1))
                        order_item = OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=item_data.get('price', product.price)
                        )
                        update_stock(product, -quantity, reason='sale')
                    except Product.DoesNotExist:
                        pass

            request.session['cart'] = {}
            _sync_abandoned_cart(request, {})

            messages.success(request, f'✅ Payment successful! Amount: ₦{amount:,.2f}')
            return redirect('products:product-list')
        else:
            error_msg = result.get('data', {}).get('gateway_response', 'Payment verification failed')
            messages.error(request, f'❌ Payment verification failed: {error_msg}')
            return redirect('products:checkout')

    except Exception as e:
        messages.error(request, f'❌ Payment error: {str(e)}')
        return redirect('products:checkout')


def index(request):
    query = request.GET.get('q') or request.GET.get('search')

    if not query:
        cached = cache.get('shop_page_data')
        if cached:
            return render(request, 'index.html', cached)

    all_products = Product.objects.all().order_by('category', '-id')

    if query:
        all_products = all_products.filter(name__icontains=query)

    products_by_category = {}
    available_categories = []

    HOMEPAGE_LIMIT = 10

    for product in all_products:
        code = product.category or 'Uncategorized'

        if query and query.lower() not in product.name.lower():
            continue

        if code not in products_by_category:
            products_by_category[code] = {'label': code, 'products': [], 'total': 0}
            available_categories.append((code, code))

        products_by_category[code]['total'] += 1

        if len(products_by_category[code]['products']) < HOMEPAGE_LIMIT:
            products_by_category[code]['products'].append(product)

    available_categories.sort(key=lambda x: x[1])

    latest_products = list(Product.objects.order_by('-id')[:8])

    wishlisted_ids = []
    if request.user.is_authenticated:
        wishlisted_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'products_by_category': products_by_category,
        'query': query,
        'available_categories': available_categories,
        'latest_products': latest_products,
        'wishlisted_ids': wishlisted_ids,
        'total_products': Product.objects.count(),
    }

    if not query:
        cache.set('shop_page_data', context, 300)

    return render(request, 'index.html', context)


def landing_page(request):
    featured_products = Product.objects.all().order_by('-id')[:6]

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

        user = User.objects.create_user(username=username, email=email, password=password)
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

    return render(request, 'landing.html', {'featured_products': featured_products})


def login_page(request):
    return login_enhanced(request)


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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('products:password-reset-done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    from_email = 'afolabiprosper329@gmail.com'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('products:login')
    post_reset_login = True


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

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, "✅ Account created! Please log in.")
        return redirect('products:login')

    return render(request, 'register.html')


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

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, f"✅ Account created! Welcome, {username}. Please log in.")
        return redirect('products:login')

    return render(request, 'auth/register_enhanced.html')


def logout_page(request):
    logout(request)
    messages.success(request, "👋 You have been logged out successfully.")
    return redirect('products:product-list')


@login_required(login_url='products:login')
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    loyalty_points = sum(int(order.total // 500) for order in orders if order.is_paid)
    referral_link = request.build_absolute_uri(reverse('products:landing'))
    if user.username:
        referral_link += f'?ref={user.username}'

    messages.info(request, f"Welcome to your profile! You have {orders.count()} orders.")
    return render(request, 'profile.html', {
        'user': user,
        'orders': orders,
        'order_count': orders.count(),
        'loyalty_points': loyalty_points,
        'referral_link': referral_link,
    })


def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    if product.is_out_of_stock:
        messages.error(request, f"⚠️ {product.name} is out of stock.")
        return redirect('products:product-detail', product_id=product.id)

    cart = request.session.get('cart', {})
    product_id = str(product.id)

    if product.has_active_sale:
        price = float(product.sale_price)
    else:
        price = float(product.price)

    if product_id in cart:
        cart[product_id]['quantity'] = cart[product_id]['quantity'] + 1
    else:
        cart[product_id] = {
            'quantity': 1,
            'price': price,
            'name': product.name,
            'image': product.image_src
        }

    request.session['cart'] = cart
    _sync_abandoned_cart(request, cart)

    messages.success(request, f"🛒 {product.name} added to your cart! (₦{price:.2f})")
    return redirect('products:product-list')


def _get_cart_products(request, cart):
    products = []
    total = 0
    invalid_item_ids = []

    for product_id, item_data in list(cart.items()):
        try:
            product = Product.objects.get(id=int(product_id))
        except (Product.DoesNotExist, ValueError, TypeError):
            invalid_item_ids.append(product_id)
            continue

        quantity = item_data.get('quantity', 1)
        price = item_data.get('price', product.sale_price if product.has_active_sale else product.price)
        product.quantity = quantity
        product.cart_price = price
        product.total_price = price * quantity
        products.append(product)
        total += product.total_price

    if invalid_item_ids:
        for invalid_id in invalid_item_ids:
            cart.pop(invalid_id, None)
        request.session['cart'] = cart
        _sync_abandoned_cart(request, cart)
        messages.warning(request, "⚠️ Some unavailable items were removed from your cart.")

    return products, total


def _get_coupon_values(request, subtotal):
    coupon_code = request.session.get('coupon_code', '')
    coupon_discount = 0
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code, is_active=True).first()
        if coupon and coupon.is_valid(total=subtotal):
            coupon_discount = coupon.calculate_discount(subtotal)
        else:
            request.session.pop('coupon_code', None)
            coupon_code = ''
    return coupon_code, coupon_discount


def view_cart(request):
    cart = request.session.get('cart', {})
    products, total = _get_cart_products(request, cart)
    coupon_code, coupon_discount = _get_coupon_values(request, total)
    total_after_coupon = max(total - coupon_discount, 0)

    return render(request, 'cart.html', {
        'products': products,
        'total': total,
        'query': request.GET.get('q', ''),
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
        'total_after_coupon': total_after_coupon,
    })


def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        _sync_abandoned_cart(request, cart)
        messages.info(request, "🗑️ Item removed from your cart successfully.")
    else:
        messages.warning(request, "⚠️ Item not found in your cart.")

    return redirect('products:view-cart')


def checkout(request):
    cart = request.session.get('cart', {})
    products, total = _get_cart_products(request, cart)
    coupon_code, coupon_discount = _get_coupon_values(request, total)
    total_after_coupon = max(total - coupon_discount, 0)

    context = {
        'products': products,
        'total': total,
        'query': request.GET.get('q', ''),
        'paystack_public_key': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'total_after_coupon': total_after_coupon,
    }

    return render(request, 'checkout.html', context)


@require_http_methods(["POST"])
def apply_coupon(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        payload = {}
    code = payload.get('code') or request.POST.get('code') or request.POST.get('coupon_code')
    if not code:
        return JsonResponse({'success': False, 'error': 'Coupon code is required.'}, status=400)

    coupon = Coupon.objects.filter(code__iexact=code.strip(), is_active=True).first()
    cart = request.session.get('cart', {})
    products, total = _get_cart_products(request, cart)
    if not coupon or not coupon.is_valid(total=total):
        return JsonResponse({'success': False, 'error': 'Coupon code is not valid for your order.'}, status=400)

    request.session['coupon_code'] = coupon.code
    request.session.modified = True
    discount_amount = coupon.calculate_discount(total)
    return JsonResponse({
        'success': True,
        'message': f'Coupon "{coupon.code}" applied successfully.',
        'coupon_code': coupon.code,
        'coupon_discount': discount_amount,
        'total_after_coupon': max(total - discount_amount, 0),
    })


@require_http_methods(["POST"])
def remove_coupon(request):
    request.session.pop('coupon_code', None)
    request.session.modified = True
    return JsonResponse({'success': True, 'message': 'Coupon removed.'})


@login_required(login_url='products:login')
def reorder_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = request.session.get('cart', {})
    for item in order.items.all():
        product_id = str(item.product.id)
        cart[product_id] = {
            'quantity': item.quantity,
            'price': item.price,
            'name': item.product.name,
            'image': item.product.image_src,
        }
    request.session['cart'] = cart
    _sync_abandoned_cart(request, cart)
    messages.success(request, '🔄 Reorder added to your cart. You can review it before checkout.')
    return redirect('products:view-cart')


@login_required(login_url='products:login')
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product').all()
    context = {
        'order': order,
        'items': items,
        'user': request.user,
    }

    if request.GET.get('format') == 'pdf':
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from io import BytesIO

            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            pdf.setTitle(f'Invoice #{order.id}')
            pdf.setFont('Helvetica-Bold', 16)
            pdf.drawString(40, 740, f'Invoice #{order.id}')
            pdf.setFont('Helvetica', 10)
            pdf.drawString(40, 720, f'Date: {order.created_at.strftime("%Y-%m-%d")}')
            pdf.drawString(40, 704, f'Customer: {request.user.get_full_name() or request.user.username}')
            pdf.drawString(40, 688, f'Email: {request.user.email}')
            y = 660
            pdf.drawString(40, y, 'Product')
            pdf.drawString(300, y, 'Qty')
            pdf.drawString(360, y, 'Unit')
            pdf.drawString(440, y, 'Total')
            y -= 18
            for item in items:
                pdf.drawString(40, y, item.product.name[:35])
                pdf.drawString(300, y, str(item.quantity))
                pdf.drawString(360, y, f'₦{item.price:.2f}')
                pdf.drawString(440, y, f'₦{item.total_price:.2f}')
                y -= 16
                if y < 80:
                    pdf.showPage()
                    y = 740
            y -= 14
            pdf.drawString(40, y, f'Subtotal: ₦{order.subtotal:.2f}')
            pdf.drawString(40, y - 14, f'Discount: ₦{order.discount:.2f}')
            pdf.drawString(40, y - 28, f'Shipping: ₦{order.shipping_cost:.2f}')
            pdf.drawString(40, y - 42, f'Total: ₦{order.total:.2f}')
            pdf.save()
            buffer.seek(0)
            pdf_response = HttpResponse(buffer, content_type='application/pdf')
            pdf_response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
            return pdf_response
        except ImportError:
            messages.warning(request, 'PDF generation is not available. Showing invoice as HTML instead.')

    return render(request, 'invoice.html', context)


@require_http_methods(["GET"])
def product_autocomplete(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(name__icontains=query).order_by('-id')[:10]

    return JsonResponse({
        'success': True,
        'results': [
            {
                'id': product.id,
                'name': product.name,
                'price': f'{product.sale_price if product.has_active_sale else product.price:.2f}',
                'image_src': product.image_src,
                'category': product.category,
            }
            for product in products
        ]
    })


def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "✅ Payment confirmed! Thank you for shopping with RedCart.")
        request.session['cart'] = {}
        _sync_abandoned_cart(request, {})
        return redirect('products:product-list')
    return redirect('products:checkout')


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

    ai_recommendations = get_product_recommendations_ai(product, limit=4)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'additional_images': additional_images,
        'query': request.GET.get('q', ''),
        'is_in_wishlist': is_in_wishlist,
        'ai_recommendations': ai_recommendations,
    })


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.is_out_of_stock:
        messages.error(request, f"⚠️ {product.name} is out of stock.")
        return redirect('products:product-detail', product_id=product.id)

    if product.has_active_sale:
        price = float(product.sale_price)
    else:
        price = float(product.price)

    cart = {
        str(product.id): {
            'quantity': 1,
            'price': price,
            'name': product.name,
            'image': product.image_src
        }
    }
    request.session['cart'] = cart
    _sync_abandoned_cart(request, cart)
    messages.success(request, f"🛍️ {product.name} added for checkout!")
    return redirect('products:checkout')


def contact_us(request):
    from .models import ContactFormSubmission
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if all([name, email, subject, message]):
            ContactFormSubmission.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, "✅ Thank you! We've received your message. We'll respond within 24 hours.")
            return redirect('products:contact')
        else:
            messages.error(request, "❌ Please fill in all fields.")

    return render(request, 'contact.html')


def faq(request):
    from .models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    categories = set(faq.category for faq in faqs)
    category = request.GET.get('category')
    if category:
        faqs = faqs.filter(category=category)
    return render(request, 'faq.html', {'faqs': faqs, 'categories': categories, 'selected_category': category})


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
                user=request.user, order=order, title=title,
                description=description, priority=priority
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
            TicketReply.objects.create(ticket=ticket, message=message, is_admin_reply=False)
            messages.success(request, "✅ Your reply has been added.")
            return redirect('products:ticket-detail', ticket_id=ticket.id)

    return render(request, 'support/ticket_detail.html', {'ticket': ticket, 'replies': replies})


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
                user=request.user, full_name=full_name, phone=phone,
                street_address=street_address, city=city, state=state,
                postal_code=postal_code, address_type=address_type, is_default=is_default
            )
            messages.success(request, "✅ Address added successfully!")
            return redirect('products:addresses')
        else:
            messages.error(request, "❌ Please fill in all required fields.")

    return render(request, 'account/add_address.html')


@login_required(login_url='products:login')
def payment_methods(request):
    from .models import PaymentMethod
    methods = PaymentMethod.objects.filter(user=request.user)
    return render(request, 'account/payment_methods.html', {'methods': methods})


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

    return render(request, 'admin/dashboard.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_views': total_views,
        'trending_products': trending,
    })


def newsletter_signup(request):
    if request.method == 'POST':
        from .models import Newsletter
        from .utils import send_newsletter_confirmation_email

        email = request.POST.get('email', '').strip()
        if email:
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            if not created and not newsletter.subscribed:
                newsletter.subscribed = True
                newsletter.save()
                created = True

            if created:
                email_sent = send_newsletter_confirmation_email(email)
                if email_sent:
                    messages.success(request, "✅ Successfully subscribed to our newsletter! Check your inbox for a confirmation email.")
                else:
                    messages.success(request, "✅ Successfully subscribed to our newsletter! We could not send the confirmation email right now.")
            else:
                messages.info(request, "📧 You're already subscribed!")
            return redirect('products:product-list')
        else:
            messages.error(request, "❌ Please provide a valid email address.")
            return redirect('products:product-list')
    
    messages.error(request, "❌ Invalid request method.")
    return redirect('products:product-list')


def newsletter_unsubscribe(request):
    from .models import Newsletter

    email = request.GET.get('email', '').strip()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            newsletter = Newsletter.objects.filter(email__iexact=email).first()
            if newsletter and newsletter.subscribed:
                newsletter.subscribed = False
                newsletter.save()
                messages.success(request, "✅ Your email has been unsubscribed from the newsletter.")
            elif newsletter:
                messages.info(request, "ℹ️ This email is already unsubscribed.")
            else:
                messages.info(request, "❌ We couldn't find that email in our subscriber list.")
            return redirect('products:newsletter-unsubscribe')

    return render(request, 'newsletter_unsubscribe.html', {'email': email})


# ============ EMAIL DELIVERY TEST ============

def test_email(request):
    try:
        send_mail(
            'RedCart Test Email',
            'This is a test email to check delivery.',
            settings.DEFAULT_FROM_EMAIL,
            ['your-real-email@gmail.com'],  # put an email you can actually check
            fail_silently=False,
        )
        return HttpResponse('SUCCESS: send_mail did not raise an error.')
    except Exception as e:
        return HttpResponse(f'<pre>ERROR: {str(e)}\n\n{traceback.format_exc()}</pre>')


# ============ EMAIL PREVIEWS ============

def preview_email_welcome(request):
    return render(request, 'emails/welcome.html', {'site_name': 'RedCart', 'username': 'John Doe'})


def preview_email_order_confirmation(request):
    sample_order = type('Order', (), {
        'id': 12345, 'created_at': timezone.now(),
        'get_status_display': 'Pending', 'total': 150.00,
    })()
    sample_item = type('OrderItem', (), {
        'product': type('Product', (), {'name': 'Sample Product'}),
        'quantity': 2, 'price': 75.00, 'total_price': 150.00,
    })()
    return render(request, 'emails/order_confirmation.html', {
        'order': sample_order, 'items': [sample_item], 'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    })


def preview_email_order_shipped(request):
    return render(request, 'emails/order_shipped.html', {
        'order': type('Order', (), {'id': 12345, 'shipped_date': timezone.now(), 'tracking_number': 'TRK123456789'}),
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    })


def preview_email_order_delivered(request):
    return render(request, 'emails/order_delivered.html', {
        'order': type('Order', (), {'id': 12345, 'delivered_date': timezone.now()}),
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
    })


def preview_email_contact_reply(request):
    return render(request, 'emails/contact_reply.html', {
        'name': 'John Doe', 'subject': 'Question about shipping costs',
        'reply': 'Thank you for contacting us...', 'site_name': 'RedCart',
    })


def preview_email_password_reset(request):
    return render(request, 'emails/password_reset.html', {
        'site_name': 'RedCart',
        'user': type('User', (), {'first_name': 'John', 'username': 'johndoe'}),
        'reset_link': 'http://127.0.0.1:8000/products/password-reset/',
    })


# ============ NEW PAGES ============

def blog_page(request):
    articles = [
        {'id': 1, 'title': 'Top 10 Shopping Tips for Smart Buyers', 'excerpt': 'Learn how to shop smarter and save more with these proven strategies...', 'date': '2024-04-15', 'author': 'Sarah Johnson', 'category': 'Shopping Tips', 'image_emoji': '💡', 'slug': 'top-10-shopping-tips'},
        {'id': 2, 'title': 'How to Choose the Right Product', 'excerpt': 'A comprehensive guide to selecting products that match your needs and budget...', 'date': '2024-04-10', 'author': 'Michael Smith', 'category': 'Buying Guide', 'image_emoji': '🛍️', 'slug': 'how-to-choose-product'},
        {'id': 3, 'title': 'The Benefits of Free Shipping', 'excerpt': 'Discover why free shipping saves you money and improves your shopping experience...', 'date': '2024-04-05', 'author': 'Emma Wilson', 'category': 'Promotions', 'image_emoji': '🚚', 'slug': 'benefits-free-shipping'},
        {'id': 4, 'title': 'Seasonal Sales Guide', 'excerpt': 'Plan your purchases around our biggest sales events of the year...', 'date': '2024-03-28', 'author': 'Alex Brown', 'category': 'Deals', 'image_emoji': '🎉', 'slug': 'seasonal-sales-guide'},
    ]
    return render(request, 'blog.html', {'articles': articles, 'total_articles': len(articles)})


def reviews_page(request):
    products_with_reviews = Product.objects.filter(comment__isnull=False).distinct()[:8]
    all_comments = Comment.objects.all().order_by('-created_at')[:20]
    total_reviews = Comment.objects.count()
    return render(request, 'reviews.html', {
        'products_with_reviews': products_with_reviews,
        'recent_reviews': all_comments,
        'total_reviews': total_reviews,
        'average_rating': 4.5,
    })


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
            display_price = product.sale_price if product.has_active_sale else product.price
            products.append({
                'id': product.id, 'name': product.name,
                'image_src': product.image_src,
                'price': f"{display_price:.2f}",
                'is_out_of_stock': product.is_out_of_stock,
            })
        if len(products) >= 6:
            break
    return JsonResponse({'success': True, 'recently_viewed': products})


def wishlist_page(request):
    wishlist_items = []
    message = None
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        if not wishlist_items:
            message = 'Your wishlist is empty. Start adding products!'
    else:
        message = 'Log in to view and save your wishlist items.'
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items,
        'total_wishlist': wishlist_items.count() if request.user.is_authenticated else 0,
        'message': message,
    })


def about_page(request):
    company_info = {
        'name': 'RedCart', 'tagline': 'Shop Smart, Live Better',
        'description': 'Your trusted online marketplace for quality products at unbeatable prices.',
        'founded': '2020', 'email': 'afolabiprosper329@gmail.com',
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
    return render(request, 'about.html', {'company': company_info, 'stats': stats, 'team': team_members})


# ============ LEGAL PAGES & CATEGORY PAGES ============

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'legal/terms_of_service.html')


def cookie_policy(request):
    return render(request, 'legal/cookie_policy.html')


def category_page(request, category_slug):
    category_mapping = {
        'electronics': 'Electronics',
        'clothing': 'Clothing',
        'home-kitchen': 'Home',
        'sports': 'Sports',
        'books': 'Books',
        'toys': 'Toys',
        'accessories': 'Accessories',
        'fashion': 'Fashion',
        'fitness': 'Fitness',
        'gaming': 'Gaming',
        'home-appliances': 'Home Appliances',
        'laptops': 'Laptops',
        'phones': 'Phones',
        'sneakers': 'Sneakers',
        'watches': 'Watches',
        'beauty': 'Beauty',
    }

    category_name = category_mapping.get(category_slug.lower(), category_slug.title())
    products = Product.objects.filter(category__iexact=category_name)

    if not products.exists():
        products = Product.objects.filter(category__icontains=category_name)

    all_categories = Product.objects.values_list('category', flat=True).distinct()
    available_categories = sorted(set([c for c in all_categories if c]))

    context = {
        'category_name': category_name,
        'category_slug': category_slug,
        'products': products,
        'product_count': products.count(),
        'available_categories': available_categories,
    }
    return render(request, 'products/category_page.html', context)


# ============ NOTIFICATION SYSTEM VIEWS ============

def notification_center(request):
    if not request.user.is_authenticated:
        return render(request, 'notifications/notification_center_guest.html')
    return render(request, 'notifications/notification_center.html')


@require_http_methods(["GET"])
def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    notification_type = request.GET.get('type', 'all')
    is_read = request.GET.get('is_read', None)

    notifications = Notification.objects.filter(user=request.user)

    if notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)

    if is_read is not None:
        notifications = notifications.filter(is_read=is_read == 'true')

    paginator = Paginator(notifications, per_page)
    notifications_page = paginator.get_page(page)

    data = {
        'success': True,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'read_at': n.read_at.isoformat() if n.read_at else None,
                'order_id': n.order.id if n.order else None,
                'product_id': n.product.id if n.product else None,
                'ticket_id': n.ticket.id if n.ticket else None,
            }
            for n in notifications_page
        ],
        'total': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
    }
    return JsonResponse(data)


@require_http_methods(["GET"])
def get_unread_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': True, 'unread_count': 0})

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': count})


@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)


@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    updated = Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return JsonResponse({'success': True, 'marked_count': updated})


@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return JsonResponse({'success': True, 'message': 'Notification deleted'})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)


@require_http_methods(["POST"])
def clear_all_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    deleted = Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True, 'deleted_count': deleted[0] if deleted else 0})


@require_http_methods(["GET"])
def get_notification_settings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    settings_obj, created = UserNotificationSettings.objects.get_or_create(user=request.user)
    data = {
        'success': True,
        'settings': {
            'email_order_updates': settings_obj.email_order_updates,
            'email_promotions': settings_obj.email_promotions,
            'email_newsletter': settings_obj.email_newsletter,
            'email_support_replies': settings_obj.email_support_replies,
            'push_order_updates': settings_obj.push_order_updates,
            'push_promotions': settings_obj.push_promotions,
            'push_low_stock_alerts': settings_obj.push_low_stock_alerts,
            'sound_enabled': settings_obj.sound_enabled,
            'sound_volume': settings_obj.sound_volume,
            'desktop_notifications': settings_obj.desktop_notifications,
            'dnd_enabled': settings_obj.dnd_enabled,
            'dnd_start_time': settings_obj.dnd_start_time.strftime('%H:%M') if settings_obj.dnd_start_time else None,
            'dnd_end_time': settings_obj.dnd_end_time.strftime('%H:%M') if settings_obj.dnd_end_time else None,
        }
    }
    return JsonResponse(data)


@require_http_methods(["POST"])
def update_notification_settings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    try:
        data = json.loads(request.body)
        settings_obj, created = UserNotificationSettings.objects.get_or_create(user=request.user)

        for key, value in data.items():
            if hasattr(settings_obj, key):
                setattr(settings_obj, key, value)

        settings_obj.save()
        return JsonResponse({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def test_notification(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    notification = Notification.objects.create(
        user=request.user,
        title="Test Notification",
        message="Your notification system is working perfectly! 🎉",
        notification_type="success"
    )

    return JsonResponse({
        'success': True,
        'message': 'Test notification sent!',
        'notification_id': notification.id
    })


def get_vapid_public_key(request):
    return JsonResponse({
        'success': True,
        'public_key': settings.VAPID_PUBLIC_KEY if hasattr(settings, 'VAPID_PUBLIC_KEY') else ''
    })


@csrf_exempt
@require_http_methods(["POST"])
def subscribe_push_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        p256dh = data.get('keys', {}).get('p256dh')
        auth = data.get('keys', {}).get('auth')

        PushNotificationSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': p256dh,
                'auth': auth,
                'is_active': True,
            }
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def unsubscribe_push_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)

    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')

        if endpoint:
            PushNotificationSubscription.objects.filter(
                endpoint=endpoint,
                user=request.user
            ).update(is_active=False)

        return JsonResponse({'success': True, 'message': 'Unsubscribed successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_system_alerts(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    alerts = SystemAlert.objects.filter(
        is_active=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-created_at')

    data = {
        'success': True,
        'alerts': [
            {
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'type': alert.alert_type,
                'trigger_type': alert.trigger_type,
                'trigger_data': alert.trigger_data,
                'created_at': alert.created_at.isoformat(),
            }
            for alert in alerts
        ]
    }
    return JsonResponse(data)


@require_http_methods(["POST"])
def dismiss_system_alert(request, alert_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        alert = SystemAlert.objects.get(id=alert_id)
        alert.is_active = False
        alert.save()
        return JsonResponse({'success': True, 'message': 'Alert dismissed'})
    except SystemAlert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)


def create_notification(user, title, message, notification_type='info', order=None, product=None, ticket=None):
    if not user or not user.is_authenticated:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        order=order,
        product=product,
        ticket=ticket
    )
