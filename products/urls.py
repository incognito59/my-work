from django.urls import path
from . import views

app_name = 'products'  # Namespace for cleaner referencing

urlpatterns = [
    path('', views.index, name='product-list'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.view_cart, name='view-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),  # ✅ Add this line
]
