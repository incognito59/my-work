from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django auth URLs (password reset etc.)
    path('auth/', include('django.contrib.auth.urls')),

    # Firebase token verification endpoint
    path('auth/google/callback/', product_views.firebase_auth_callback, name='firebase-auth-callback'),

    # Allauth URLs (Google, Facebook, GitHub login)
    path('accounts/', include('allauth.urls')),

    path('api/chat/', product_views.ai_chat, name='api-chat-root'),

    # Paystack payment verification
    path('products/payment/verify/', product_views.paystack_verify, name='paystack-verify'),

    # Primary product routes
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # Root redirect
    path('', RedirectView.as_view(pattern_name='products:product-list', permanent=False)),

    # Convenience redirects
    path('login/', RedirectView.as_view(pattern_name='products:login', permanent=False)),
    path('register/', RedirectView.as_view(pattern_name='products:register', permanent=False)),
    path('cart/', RedirectView.as_view(pattern_name='products:view-cart', permanent=False)),
    path('checkout/', RedirectView.as_view(pattern_name='products:checkout', permanent=False)),
    path('product/<int:product_id>/', RedirectView.as_view(pattern_name='products:product-detail', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)