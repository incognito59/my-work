from django.urls import path
from . import views

<<<<<<< HEAD
app_name = 'products'  # For namespacing URL names
=======
app_name = 'products'  
>>>>>>> c38250015cc0dc8e8692c53443fead5b2b558d68

urlpatterns = [
    path('', views.index, name='product-list'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.view_cart, name='view-cart'),
    path('checkout/', views.checkout, name='checkout'),
<<<<<<< HEAD
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),  # ✅ Detail view
=======
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),  
>>>>>>> c38250015cc0dc8e8692c53443fead5b2b558d68
]
