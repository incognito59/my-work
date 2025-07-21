from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def login_page(request):
    if request.method == 'POST':
        return redirect('products:product-list')
    return render(request, 'login.html')

def register_page(request):
    if request.method == 'POST':
        return redirect('products:login')
    return render(request, 'register.html')

def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    cart = request.session.get('cart', [])
    cart.append(product.id)
    request.session['cart'] = cart
    return redirect('products:product-list')

def view_cart(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    total = sum(product.price for product in products)
    return render(request, 'cart.html', {'products': products, 'total': total})

def checkout(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    total = sum(product.price for product in products)
    total_kobo = int(total * 100)

    context = {
        'products': products,
        'total': total,
        'total_kobo': total_kobo,
        'paystack_public_key': 'pk_test_your_public_key_here'  
    }
    return render(request, 'checkout.html', context)

def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "Payment confirmed. Thank you!")
        request.session['cart'] = []  
        return redirect('products:product-list')

# ✅ Corrected detail view
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})
