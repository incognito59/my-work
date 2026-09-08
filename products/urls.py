from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 🎯 Landing Page (Home)
    path('', views.landing_page, name='landing'),
    path('landing/', views.landing_page, name='landing-alt'),
    
    # 🔍 Product pages
    path('shop/', views.index, name='product-list'),
    path('intelligence/', views.security_intelligence, name='security-intelligence'),
    path('api/shodan/intelligence/', views.shodan_intelligence_api, name='api-shodan-intelligence'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit-review'),

    # 🛒 Cart actions
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add-to-cart'),
    path('delete-from-cart/<int:product_id>/', views.delete_from_cart, name='delete-from-cart'),
    path('cart/', views.view_cart, name='view-cart'),

    # 💳 Checkout & payments
    path('checkout/', views.checkout, name='checkout'),
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('api/apply-coupon/', views.apply_coupon, name='api-apply-coupon'),
    path('api/remove-coupon/', views.remove_coupon, name='api-remove-coupon'),
    path('api/autocomplete/', views.product_autocomplete, name='api-autocomplete'),
    path('order/<int:order_id>/reorder/', views.reorder_order, name='reorder-order'),
    path('order/<int:order_id>/invoice/', views.order_invoice, name='order-invoice'),
    path('order/<int:order_id>/escrow/release/', views.release_escrow, name='release-escrow'),
    path('order/<int:order_id>/escrow/dispute/', views.dispute_escrow, name='dispute-escrow'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy-now'),

    # 👤 Auth pages
    path('login/', views.login_enhanced, name='login'),
    path('register/', views.register_enhanced, name='register'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('account/', views.account_dashboard, name='account-dashboard'),
    
    # 🏠 Account Management
    path('addresses/', views.addresses, name='addresses'),
    path('add-address/', views.add_address, name='add-address'),
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit-address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete-address'),
    path('payment-methods/', views.payment_methods, name='payment-methods'),
    path('wallet/', views.wallet, name='wallet'),
    path('wallet/topup/verify/', views.wallet_topup_verify, name='wallet-topup-verify'),
    
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
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter-unsubscribe'),

    # 📝 Blog & Content Pages
    path('blog/', views.blog_page, name='blog'),
    path('reviews/', views.reviews_page, name='reviews'),
    path('api/chat/', views.ai_chat, name='api-chat'),
    path('ai-chat/', views.ai_chat, name='ai-chat'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle-wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('about/', views.about_page, name='about'),
    
    # 📧 Email Templates Preview (Development/Testing) - Direct & Aliased URLs
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
    
    # 🔄 Recently Viewed
    path('api/recently-viewed/', views.recently_viewed, name='api-recently-viewed'),
    
    # ============ NOTIFICATION SYSTEM URLS ============
    
    # 🔔 Notification Endpoints
    path('api/notifications/', views.get_notifications, name='api-notifications'),
    path('api/notifications/unread/count/', views.get_unread_count, name='api-notifications-count'),
    path('api/notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='api-notifications-mark-read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='api-notifications-mark-all-read'),
    path('api/notifications/delete/<int:notification_id>/', views.delete_notification, name='api-notifications-delete'),
    path('api/notifications/clear-all/', views.clear_all_notifications, name='api-notifications-clear-all'),
    
    # ⚙️ Notification Settings
    path('api/notification-settings/', views.get_notification_settings, name='api-notification-settings'),
    path('api/notification-settings/update/', views.update_notification_settings, name='api-notification-settings-update'),
    
    # 📱 Push Notifications
    path('api/push/subscribe/', views.subscribe_push_notifications, name='api-push-subscribe'),
    path('api/push/unsubscribe/', views.unsubscribe_push_notifications, name='api-push-unsubscribe'),
    path('api/push/vapid-public-key/', views.get_vapid_public_key, name='api-push-vapid-key'),
    
    # 🔔 Notification Center UI
    path('notifications/', views.notification_center, name='notification-center'),
    
    # 🎵 Test Sound
    path('api/test-notification/', views.test_notification, name='api-test-notification'),
    
    # 📊 Admin System Alerts
    path('api/system-alerts/', views.get_system_alerts, name='api-system-alerts'),
    path('api/system-alerts/dismiss/<int:alert_id>/', views.dismiss_system_alert, name='api-system-alerts-dismiss'),
    
    # ============ LEGAL PAGES & CATEGORY PAGES ============
    
    # 📜 Legal Pages
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-of-service/', views.terms_of_service, name='terms-of-service'),
    path('cookie-policy/', views.cookie_policy, name='cookie-policy'),
    path('buyer-protection/', views.buyer_protection, name='buyer-protection'),
    
    # 🏷️ Category Pages
    path('category/<slug:category_slug>/', views.category_page, name='category-page'),
]
