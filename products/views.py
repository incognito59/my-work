from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Comment

def index(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
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
    cart = request.session.get('cart', {})

    if str(product.id) in cart:
        cart[str(product.id)] += 1
    else:
        cart[str(product.id)] = 1

    request.session['cart'] = cart
    return redirect('products:view-cart')

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

    return render(request, 'cart.html', {'products': products, 'total': total})

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
        'paystack_public_key': 'pk_test_your_public_key_here'
    }
    return render(request, 'checkout.html', context)

def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "Payment confirmed. Thank you!")
        request.session['cart'] = {}
        return redirect('products:product-list')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Handle additional images if the relation exists
    try:
        additional_images = product.additional_images.all()
    except AttributeError:
        additional_images = []

    comments = product.comments.all().order_by('-created_at')

    if request.method == 'POST':
        name = request.POST.get('name')
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        if name and text and rating:
            Comment.objects.create(product=product, name=name, text=text, rating=rating)
            messages.success(request, "Thank you for your review!")
            return redirect('products:product-detail', product_id=product.id)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'additional_images': additional_images
    })

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['cart'] = {str(product.id): 1}
    return redirect('products:checkout')