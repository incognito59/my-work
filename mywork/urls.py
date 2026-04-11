"""
URL configuration for mywork project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django auth URLs (for password reset)
    path('auth/', include('django.contrib.auth.urls')),

    # Primary product routes under /products/ (namespaced)
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # Root route redirects to /products/
    path('', RedirectView.as_view(pattern_name='products:product-list', permanent=False)),

    # Convenience redirects for common legacy root paths
    path('login/', RedirectView.as_view(pattern_name='products:login', permanent=False)),
    path('register/', RedirectView.as_view(pattern_name='products:register', permanent=False)),
    path('cart/', RedirectView.as_view(pattern_name='products:view-cart', permanent=False)),
    path('checkout/', RedirectView.as_view(pattern_name='products:checkout', permanent=False)),
    path('product/<int:product_id>/', RedirectView.as_view(pattern_name='products:product-detail', permanent=False)),
]
