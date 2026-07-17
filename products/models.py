from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.utils import timezone

class Product(models.Model):
    CATEGORY_CHOICES = [
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Home', 'Home & Kitchen'),
    ('Sports', 'Sports & Outdoors'),
    ('Books', 'Books'),
    ('Toys', 'Toys & Games'),
    ('Accessories', 'Accessories'),
    ('Fashion', 'Fashion'),
    ('Fitness', 'Fitness'),
    ('Gaming', 'Gaming'),
    ('Home Appliances', 'Home Appliances'),
    ('Laptops', 'Laptops'),
    ('Phones', 'Phones'),
    ('Sneakers', 'Sneakers'),
    ('Watches', 'Watches'),
    ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    stock_quantity = models.IntegerField(null=True, blank=True, help_text='Physical stock quantity. Falls back to legacy stock when empty.')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    image_url = models.CharField("Main Image", max_length=2083)
    description = models.TextField(blank=True)

    # Optional additional image fields
    image_2 = models.CharField("Image 2", max_length=2083, blank=True, null=True)
    image_3 = models.CharField("Image 3", max_length=2083, blank=True, null=True)

    # Flash Sale Fields
    sale_price = models.FloatField(null=True, blank=True, help_text="Sale price for flash sale")
    sale_ends_at = models.DateTimeField(null=True, blank=True, help_text="End time for flash sale")

    @property
    def image_src(self):
      if self.image_url:
        if self.image_url.startswith(('http://', 'https://', '//', 'data:image')):
            return self.image_url
        return static(self.image_url)
        return 'https://via.placeholder.com/500x350?text=No+Image'
    @property
    def additional_images(self):
        images = []
        for img in [self.image_2, self.image_3]:
            if not img:
                continue
            if img.startswith(('http://', 'https://', '//')):
                images.append(img)
            else:
                images.append(static(img))
        return images

    @property
    def has_active_sale(self):
        """Check if product has an active flash sale"""
        from django.utils import timezone
        if self.sale_price is not None and self.sale_ends_at and self.price > 0:
            if self.sale_price >= self.price:
                return False
            return self.sale_ends_at > timezone.now()
        return False

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.sale_price is not None and self.price > 0 and self.sale_price < self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return max(0, round(discount, 0))
        return 0

    @property
    def available_stock(self):
        if self.stock_quantity is not None:
            return self.stock_quantity
        return self.stock

    @property
    def is_out_of_stock(self):
        return self.available_stock <= 0

    @property
    def is_low_stock(self):
        return 0 < self.available_stock <= 5

    @property
    def average_review_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        return round(sum(review.rating for review in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        return self.reviews.count()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_price = None
        if not is_new:
            previous_price = Product.objects.filter(pk=self.pk).values_list('price', flat=True).first()

        super().save(*args, **kwargs)

        if is_new:
            PriceHistory.objects.get_or_create(product=self, price=self.price, defaults={'recorded_at': timezone.now()})
            return

        if previous_price is not None and previous_price != self.price:
            PriceHistory.objects.create(product=self, price=self.price, recorded_at=timezone.now())

    def __str__(self):
        return self.name


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.FloatField()
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.product.name} - ₦{self.price} at {self.recorded_at}"


class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()

    def __str__(self):
        return self.code

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='fixed')
    discount_value = models.FloatField()
    min_order_amount = models.FloatField(default=0)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code.upper()

    def is_valid(self, total=0):
        if not self.is_active:
            return False
        if self.expiry_date <= timezone.now():
            return False
        if total < self.min_order_amount:
            return False
        return True

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            return min(subtotal, subtotal * (self.discount_value / 100))
        return min(subtotal, self.discount_value)

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} stars on {self.product.name}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_purchase = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.rating}★ for {self.product.name}"

    @property
    def average_rating(self):
        return self.rating

    @property
    def stars(self):
        return range(1, self.rating + 1)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ❤ {self.product.name}"

class Compare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compare_list')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} comparing {self.product.name}"

# 📦 Inventory Management
class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    quantity_changed = models.IntegerField()
    reason = models.CharField(max_length=100)  # 'sale', 'return', 'restock', 'adjustment'
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity_changed} ({self.reason})"


# 👕 Product Variants (Sizes, Colors, etc.)
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50, blank=True)  # 'S', 'M', 'L', 'XL', etc.
    color = models.CharField(max_length=50, blank=True)  # 'Red', 'Blue', etc.
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    price_adjustment = models.FloatField(default=0)  # Additional cost for variant
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'size', 'color')
    
    def __str__(self):
        return f"{self.product.name} - {self.size} {self.color}".strip()
    
    @property
    def final_price(self):
        return self.product.price + self.price_adjustment


# 🏠 User Address Book
class UserAddress(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nigeria')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'User Addresses'
    
    def __str__(self):
        return f"{self.full_name} - {self.street_address}"


# 💳 Payment Methods
class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # For card payments
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)  # Visa, Mastercard, etc.
    
    # For bank transfers
    bank_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_type}"


# 📦 Enhanced Order Model
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Address Info
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Order Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    
    # Payment
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pricing
    subtotal = models.FloatField(default=0)
    shipping_cost = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    insurance_opted = models.BooleanField(default=False)
    insurance_cost = models.FloatField(default=0)
    is_paid = models.BooleanField(default=False)

    # Escrow / Buyer Protection
    escrow_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Escrow'),
            ('held', 'Held in Escrow'),
            ('released', 'Released to Seller'),
            ('disputed', 'Disputed'),
        ],
        default='pending'
    )
    escrow_release_date = models.DateTimeField(null=True, blank=True)
    escrow_notes = models.TextField(blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def total(self):
        if self.subtotal:
            return self.subtotal + self.shipping_cost + self.tax + self.insurance_cost - self.discount

        item_total = sum(item.total_price for item in self.items.all())
        return item_total + self.shipping_cost + self.tax + self.insurance_cost - self.discount

    @property
    def estimated_delivery_date(self):
        if self.delivered_date:
            return self.delivered_date
        if self.shipped_date:
            return self.shipped_date + timedelta(days=3)
        return self.created_at + timedelta(days=5)

    def release_escrow_if_delivered(self):
        if self.status == 'delivered' and self.is_paid and self.escrow_status in {'held', 'pending'}:
            self.escrow_status = 'released'
            self.escrow_release_date = timezone.now()
            self.escrow_notes = 'Escrow released automatically after delivery confirmation.'
            return True
        return False

    def save(self, *args, **kwargs):
        if self.status == 'delivered' and self.is_paid and self.escrow_status in {'held', 'pending'}:
            self.escrow_status = 'released'
            self.escrow_release_date = self.escrow_release_date or timezone.now()
            if not self.escrow_notes:
                self.escrow_notes = 'Escrow released automatically after delivery confirmation.'
        super().save(*args, **kwargs)

    @property
    def escrow_is_protected(self):
        return self.escrow_status in {'held', 'pending'} and self.is_paid

    @property
    def escrow_badge(self):
        if self.escrow_status == 'held':
            return 'Protected'
        if self.escrow_status == 'released':
            return 'Released'
        if self.escrow_status == 'disputed':
            return 'Disputed'
        return 'Pending'


class AbandonedCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abandoned_carts')
    cart_data = models.JSONField(default=dict, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Abandoned cart for {self.user.username} at {self.last_updated}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()  # Price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity


# 🚚 Shipping Methods
class ShippingMethod(models.Model):
    SHIPPING_TYPES = [
        ('standard', 'Standard (5-7 days)'),
        ('express', 'Express (2-3 days)'),
        ('overnight', 'Overnight'),
    ]
    
    name = models.CharField(max_length=100)
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPES)
    base_cost = models.FloatField()
    cost_per_kg = models.FloatField(default=0)
    estimated_days = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


# 📧 Email Template & Log
class EmailTemplate(models.Model):
    EMAIL_TYPES = [
        ('welcome', 'Welcome Email'),
        ('order_confirmation', 'Order Confirmation'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('password_reset', 'Password Reset'),
        ('newsletter', 'Newsletter'),
        ('contact_reply', 'Contact Form Reply'),
    ]
    
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email_type


class EmailLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emails')
    email_type = models.CharField(max_length=50)  # Reference to EmailTemplate.email_type
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('failed', 'Failed')], default='sent')
    
    def __str__(self):
        return f"{self.email_type} to {self.recipient}"


# 🎫 Customer Support Tickets
class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.title}"


class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply to Ticket #{self.ticket.id}"


# ❓ FAQ System
class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=100)  # 'shipping', 'returns', 'payments', etc.
    order = models.IntegerField(default=0)  # For sorting
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'FAQs'
        ordering = ['order']
    
    def __str__(self):
        return self.question


# 📊 Analytics & Product Views
class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} viewed"


class ProductRecommendation(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='recommendation')
    frequently_bought_with = models.ManyToManyField(Product, related_name='recommended_by')
    
    def __str__(self):
        return f"Recommendations for {self.product.name}"


# 📝 Contact Form Submissions
class ContactFormSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"


# 🏷️ Discount Codes
class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.FloatField()  # e.g., 10 for 10% or 1000 for ₦1000
    max_usage = models.IntegerField(null=True, blank=True)  # None = unlimited
    current_usage = models.IntegerField(default=0)
    min_purchase = models.FloatField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code
    
    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until and (self.max_usage is None or self.current_usage < self.max_usage)


# 📱 App Newsletter
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email


# ============ NOTIFICATION SYSTEM ============

class Notification(models.Model):
    """Store all user notifications"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('order', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Link to related objects
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For real-time notifications
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # For push notifications
    push_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title} for {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class UserNotificationSettings(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Email notifications
    email_order_updates = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=True)
    email_support_replies = models.BooleanField(default=True)
    
    # Push notifications
    push_order_updates = models.BooleanField(default=True)
    push_promotions = models.BooleanField(default=False)
    push_low_stock_alerts = models.BooleanField(default=True)
    
    # Sound notifications
    sound_enabled = models.BooleanField(default=True)
    sound_volume = models.IntegerField(default=70)  # 0-100
    
    # Desktop notifications
    desktop_notifications = models.BooleanField(default=True)
    
    # Do not disturb
    dnd_enabled = models.BooleanField(default=False)
    dnd_start_time = models.TimeField(null=True, blank=True)
    dnd_end_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"


class PushNotificationSubscription(models.Model):
    """Store browser push notification subscriptions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Push subscription for {self.user.username}"


class NotificationLog(models.Model):
    """Track all notifications sent"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    
    # Channel: web, email, push
    channel = models.CharField(max_length=20)
    
    # Status: sent, delivered, failed, read
    status = models.CharField(max_length=20, default='sent')
    
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.channel} notification to {self.user.username} at {self.sent_at}"


class SystemAlert(models.Model):
    """System-wide alerts for admin"""
    ALERT_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # For low stock, new orders, etc.
    trigger_type = models.CharField(max_length=50, blank=True)  # 'low_stock', 'new_order', etc.
    trigger_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"