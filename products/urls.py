from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 🎯 Landing Page (Home)
    path('', views.landing_page, name='landing'),
    path('landing/', views.landing_page, name='landing-alt'),
    
    # 🔍 Product pages
    path('shop/', views.index, name='product-list'),
    path('offers/', views.offers_page, name='offers'),
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
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    
    # 🏠 Account Management
    path('addresses/', views.addresses, name='addresses'),
    path('add-address/', views.add_address, name='add-address'),
    path('payment-methods/', views.payment_methods, name='payment-methods'),
    
    # 📧 Support & Communication
    path('contact/', views.contact_us, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('tickets/', views.my_tickets, name='my-tickets'),
    path('ticket/create/', views.create_ticket, name='create-ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket-detail'),
    
    # 📊 Analytics
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    
    # 📱 Newsletter
    path('newsletter/signup/', views.newsletter_signup, name='newsletter-signup'),
    
    # � Blog & Content Pages
    path('blog/', views.blog_page, name='blog'),
    path('reviews/', views.reviews_page, name='reviews'),
    path('api/chat/', views.ai_chat, name='api-chat'),
    path('ai-chat/', views.ai_chat, name='ai-chat'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle-wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('about/', views.about_page, name='about'),
    
    # �📧 Email Templates Preview (Development/Testing) - Direct & Aliased URLs
    path('preview/email/welcome/', views.preview_email_welcome, name='preview-email-welcome'),
    path('preview/email/order_confirmation/', views.preview_email_order_confirmation, name='preview-email-order-confirmation'),
    path('preview/email/order_shipped/', views.preview_email_order_shipped, name='preview-email-order-shipped'),
    path('preview/email/order_delivered/', views.preview_email_order_delivered, name='preview-email-order-delivered'),
    path('preview/email/contact_reply/', views.preview_email_contact_reply, name='preview-email-contact-reply'),
    path('preview/email/password_reset/', views.preview_email_password_reset, name='preview-email-password-reset'),
    
    # 📧 Email Templates Preview - Short URLs (Aliases for easier access)
    path('welcome/', views.preview_email_welcome, name='email-welcome'),
    path('order_confirmation/', views.preview_email_order_confirmation, name='email-order-confirmation'),
    path('order_shipped/', views.preview_email_order_shipped, name='email-order-shipped'),
    path('order_delivered/', views.preview_email_order_delivered, name='email-order-delivered'),
    path('contact_reply/', views.preview_email_contact_reply, name='email-contact-reply'),
    path('password_reset/', views.preview_email_password_reset, name='email-password-reset'),
]

