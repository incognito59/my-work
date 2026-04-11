from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 🔍 Product pages
    path('', views.index, name='product-list'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),

    # 🛒 Cart actions
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add-to-cart'),
    path('delete-from-cart/<int:product_id>/', views.delete_from_cart, name='delete-from-cart'),
    path('cart/', views.view_cart, name='view-cart'),

    # 💳 Checkout & payments
    path('checkout/', views.checkout, name='checkout'),
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy-now'),

    # 👤 Auth pages
    path('login/', views.login_enhanced, name='login'),
    path('register/', views.register_enhanced, name='register'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password-reset'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.user_profile, name='profile'),
]

