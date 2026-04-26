# Flash Sale Timer - Code Examples & Snippets

## Quick Reference for Common Tasks

### 1. Create a Flash Sale Programmatically

```python
from products.models import Product
from datetime import timedelta
from django.utils import timezone

# Get product
product = Product.objects.get(id=1)

# Set flash sale
product.sale_price = 7000  # Must be less than product.price
product.sale_ends_at = timezone.now() + timedelta(hours=2)
product.save()

# Verify
print(f"Sale Active: {product.has_active_sale}")
print(f"Discount: {product.discount_percentage}%")
print(f"Original: ₦{product.price} → Sale: ₦{product.sale_price}")
```

### 2. End a Flash Sale

```python
product = Product.objects.get(id=1)
product.sale_price = None
product.sale_ends_at = None
product.save()
```

### 3. Get All Active Flash Sales

```python
from products.models import Product

active_sales = [p for p in Product.objects.all() if p.has_active_sale]

for product in active_sales:
    print(f"{product.name}: {product.discount_percentage}% off")
```

### 4. Get Sales Ending Soon (within 1 hour)

```python
from django.utils import timezone
from datetime import timedelta

cutoff_time = timezone.now() + timedelta(hours=1)

ending_soon = [p for p in Product.objects.all() 
               if p.has_active_sale and p.sale_ends_at <= cutoff_time]

for product in ending_soon:
    remaining = product.sale_ends_at - timezone.now()
    minutes = remaining.total_seconds() / 60
    print(f"{product.name}: {minutes:.0f} minutes left")
```

### 5. Bulk Create Flash Sales

```python
from products.models import Product
from datetime import timedelta
from django.utils import timezone

products = Product.objects.filter(category='Electronics')[:5]

for product in products:
    # 25% off for 3 hours
    product.sale_price = product.price * 0.75
    product.sale_ends_at = timezone.now() + timedelta(hours=3)
    product.save()
```

### 6. Check Sale Status in Template

```html
{% if product.has_active_sale %}
    <div class="badge badge-danger">
        {{ product.discount_percentage }}% OFF
    </div>
    <p class="original-price">
        <strike>₦{{ product.price|floatformat:2 }}</strike>
    </p>
    <p class="sale-price">
        ₦{{ product.sale_price|floatformat:2 }}
    </p>
{% endif %}
```

### 7. Display Timer in Template (with automatic updates)

```html
{% if product.has_active_sale %}
<div class="flash-sale-badge" 
     data-product-id="{{ product.id }}" 
     data-sale-ends-at="{{ product.sale_ends_at|date:'c' }}">
    <div class="flash-sale-banner">
        <div class="flash-sale-label">⚡ Flash Sale</div>
        <div class="flash-sale-timer" 
             data-product-id="{{ product.id }}" 
             data-sale-ends-at="{{ product.sale_ends_at|date:'c' }}">
            Loading...
        </div>
    </div>
</div>
{% endif %}

<!-- Make sure to include the script -->
<script src="{% static 'js/flash-sale-timer.js' %}"></script>
```

### 8. Custom Timer Display (minutes only)

```python
# In your view
from django.utils import timezone

product = Product.objects.get(id=1)
if product.has_active_sale:
    remaining_seconds = (product.sale_ends_at - timezone.now()).total_seconds()
    remaining_minutes = int(remaining_seconds / 60)
    context['time_remaining_minutes'] = remaining_minutes
```

```html
<!-- In template -->
{% if remaining_minutes > 0 %}
    <p>⏰ {{ remaining_minutes }} minutes left!</p>
{% else %}
    <p>⏰ Less than 1 minute left!</p>
{% endif %}
```

### 9. Admin Command to Clean Up Expired Sales

```python
# Create file: products/management/commands/cleanup_expired_sales.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Product

class Command(BaseCommand):
    help = 'Remove expired flash sales'

    def handle(self, *args, **options):
        expired = 0
        for product in Product.objects.all():
            if product.sale_price and product.sale_ends_at <= timezone.now():
                product.sale_price = None
                product.sale_ends_at = None
                product.save()
                expired += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Cleaned up {expired} expired sales")
        )

# Run with:
# python manage.py cleanup_expired_sales
```

### 10. Send Email Alert for Sales Ending Soon

```python
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from products.models import Product

# Find sales ending in next 30 minutes
cutoff = timezone.now() + timedelta(minutes=30)

for product in Product.objects.all():
    if product.has_active_sale and product.sale_ends_at <= cutoff:
        # Send email to interested customers
        send_mail(
            subject=f'Hurry! {product.name} sale ends soon!',
            message=f'Flash sale ends in 30 minutes. Save {product.discount_percentage}%!',
            from_email='noreply@redcart.com',
            recipient_list=['customer@email.com'],
        )
```

### 11. API Response with Sale Info

```python
# In your API serializer
from rest_framework import serializers
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    has_active_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'sale_price', 'sale_ends_at', 
                  'has_active_sale', 'discount_percentage', 'effective_price')
    
    def get_has_active_sale(self, obj):
        return obj.has_active_sale
    
    def get_discount_percentage(self, obj):
        return obj.discount_percentage if obj.has_active_sale else 0
    
    def get_effective_price(self, obj):
        return obj.sale_price if obj.has_active_sale else obj.price
```

### 12. JavaScript - Reinitialize Timer After AJAX Load

```javascript
// After loading products via AJAX
fetch('/products/load-more-products/')
    .then(response => response.text())
    .then(html => {
        // Insert HTML
        document.getElementById('product-list').innerHTML += html;
        
        // Reinitialize timers for new products
        new FlashSaleTimer();
    });
```

### 13. JavaScript - Listen to Timer Events

```javascript
// Create custom timer with event handling
class CustomFlashSaleTimer extends FlashSaleTimer {
    handleSaleEnded(productId, elements) {
        // Custom behavior when sale ends
        console.log(`Sale #${productId} has ended!`);
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('saleEnded', {
            detail: { productId }
        }));
        
        // Call parent method
        super.handleSaleEnded(productId, elements);
    }
}

// Listen for sale end events
window.addEventListener('saleEnded', (e) => {
    console.log(`Product ${e.detail.productId} sale has ended`);
});
```

### 14. Change Timer Colors Dynamically

```css
/* Based on urgency level */
.flash-sale-timer.timer-urgent {
    animation: urgentPulse 0.4s ease-in-out infinite;
}

.flash-sale-timer.timer-urgent.custom-theme {
    color: #ffd700;  /* Gold */
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.8);
}
```

### 15. Testing Flash Sales

```python
# In your test file
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from products.models import Product

class FlashSaleTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=10000,
            stock=10,
            category="Electronics"
        )
    
    def test_has_active_sale_true(self):
        self.product.sale_price = 7000
        self.product.sale_ends_at = timezone.now() + timedelta(hours=1)
        self.product.save()
        
        self.assertTrue(self.product.has_active_sale)
    
    def test_has_active_sale_false(self):
        self.product.sale_price = 7000
        self.product.sale_ends_at = timezone.now() - timedelta(hours=1)
        self.product.save()
        
        self.assertFalse(self.product.has_active_sale)
    
    def test_discount_percentage(self):
        self.product.sale_price = 7000
        self.product.save()
        
        self.assertEqual(self.product.discount_percentage, 30)
```

## Useful Patterns

### Pattern 1: Time-based Pricing
```python
# Different time periods, different prices
product.sale_price = 8500  # First 2 hours: 15% off
product.sale_ends_at = timezone.now() + timedelta(hours=2)
# After 2 hours, manually update to next tier
```

### Pattern 2: Stock-based Sales
```python
# Run sale only while stock is limited
if product.stock < 20:
    product.sale_price = 8000
    product.sale_ends_at = timezone.now() + timedelta(hours=4)
```

### Pattern 3: Event-based Sales
```python
# Flash sale for specific events
from django.utils.dateparse import parse_datetime

# Black Friday, 9am - 5pm
blackfriday_end = parse_datetime('2026-11-29T17:00:00')
product.sale_price = 6000
product.sale_ends_at = blackfriday_end
```

---

**Pro Tip**: Always set `sale_price < price` or the discount won't show!
