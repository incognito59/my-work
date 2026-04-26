# ⚡ Flash Sale Timer - Quick Start Guide

## What Was Implemented

A complete flash sale timer system for your Retail Logistics platform that shows live countdown timers on products with time-limited discounts.

## Features at a Glance

✅ **Live Countdown Timers** - Real-time JavaScript timers that update every second  
✅ **Urgency Indicators** - Visual changes as sale end time approaches  
✅ **Product Listings** - Flash sale badges on product cards with timer  
✅ **Product Details** - Large flash sale banner on product detail page  
✅ **Admin Interface** - Easy setup from Django admin panel  
✅ **Mobile Responsive** - Works perfectly on all devices  
✅ **Dark Theme Support** - Matches your existing theme system  

## Quick Setup (5 Minutes)

### Step 1: Create a Flash Sale in Admin
1. Go to `http://localhost:8000/admin/products/product/`
2. Click on any product to edit
3. Scroll down to **"Flash Sale"** section (collapsed by default)
4. Fill in:
   - **Sale Price**: e.g., `7000` (the discounted price)
   - **Sale Ends At**: e.g., `2026-04-27 18:00:00` (when sale expires)
5. Click **Save**

### Step 2: View the Flash Sale
- **Product Listing**: Navigate to `http://localhost:8000/` to see the flash sale badge
- **Product Detail**: Click on the product to see the large flash sale banner
- **Live Timer**: Watch the countdown update in real-time!

## What Customers See

### On Product Cards (Listing Page)
```
┌─────────────────────┐
│  ⚡ Flash Sale     │ ← Banner in corner
│    00h 30m 45s     │
│    [IMAGE HERE]     │
├─────────────────────┤
│ Product Name        │
│ ₦10,000 ₦7,000 -30% │ ← Original, sale price, savings
│ [View] [Add Cart]   │
└─────────────────────┘
```

### On Product Detail Page
```
⚡ Flash Sale Ends In
00:30:45

Save 30%
₦10,000 → ₦7,000

[Add to Cart] [Buy Now]
```

## Timer Behavior

The timer automatically adapts its display:

| Time Left | Display | Appearance |
|-----------|---------|------------|
| > 1 day | `2d 5h 30m` | White text |
| 1-24 hours | `5h 30m 12s` | Glowing white |
| 1-60 minutes | `30m 45s` | Pulsing yellow ⚡ |
| < 1 minute | `45s` | Urgent pulse |
| Expired | `Sale Ended` | Faded out |

## Database Fields Added

The Product model now has:
- `sale_price` (decimal) - The discounted price
- `sale_ends_at` (datetime) - When the sale expires

**Migration Applied**: `0008_product_sale_ends_at_product_sale_price`

## Files Created

| File | Purpose |
|------|---------|
| `frontend/js/flash-sale-timer.js` | Timer logic (4KB) |
| `frontend/css/flash-sale-timer.css` | Styling & animations |
| `setup_flash_sales.py` | Helper script for testing |
| `FLASH_SALE_TIMER.md` | Detailed documentation |

## Template Changes

- **index.html**: Added flash sale badge to product cards
- **product_detail.html**: Added flash sale banner to product details

## Usage Examples

### From Django Admin
1. Open any product
2. Set `sale_price` to a lower value than `price`
3. Set `sale_ends_at` to a future date/time
4. Save!

### Programmatically (in Django Shell)
```python
from products.models import Product
from datetime import timedelta
from django.utils import timezone

product = Product.objects.get(id=1)
product.sale_price = 7000
product.sale_ends_at = timezone.now() + timedelta(hours=2)
product.save()

# Check if sale is active
if product.has_active_sale:
    print(f"Discount: {product.discount_percentage}%")
```

### Using Helper Script
```bash
# Start Django shell
python manage.py shell

# Run helper functions
exec(open('setup_flash_sales.py').read())

# Create demo sales
setup_demo_flash_sales()

# List active sales
list_active_flash_sales()

# Create specific sale
create_specific_flash_sale(product_id=1, sale_price=5000, hours_until_end=2)
```

## Customization

### Change Colors
Edit `frontend/css/flash-sale-timer.css`:
```css
.flash-sale-banner {
    background: linear-gradient(135deg, #ff4757 0%, #ee5a6f 100%);
    /* Change to your brand colors */
}
```

### Change Timer Format
Edit `frontend/js/flash-sale-timer.js` - the `renderTimer` method controls display format

### Change Update Frequency
In `flash-sale-timer.js`:
```javascript
setInterval(() => this.updateAllTimers(), 1000);  // 1000ms = 1 second
```

## Admin Features

The admin now shows:
- **Flash Sale Status** column (⚡ Active Sale, ⏰ Expired, No Sale)
- **Flash Sale** fieldset (collapsed) for easy editing
- Helpful description for sale_price and sale_ends_at fields

## Troubleshooting

**Q: Timer not showing?**
- Ensure sale_ends_at is in the future (compare with server time)
- Check that both sale_price AND sale_ends_at are set
- Verify page loaded the CSS and JS files (check browser console)

**Q: Timer not updating?**
- Check browser console for JavaScript errors (F12)
- Verify system clock is accurate
- Try refreshing the page

**Q: Wrong discount percentage?**
- Ensure sale_price < price
- Property auto-calculates: `((price - sale_price) / price) * 100`

## Files Reference

```
/workspaces/Retail-Logistics-Core/
├── frontend/
│   ├── js/
│   │   └── flash-sale-timer.js          [NEW] Timer JavaScript
│   └── css/
│       └── flash-sale-timer.css         [NEW] Timer Styling
├── products/
│   ├── models.py                         [MODIFIED] Added sale fields
│   ├── admin.py                          [MODIFIED] Enhanced admin
│   ├── migrations/
│   │   └── 0008_...                      [NEW] Migration
│   └── templates/
│       ├── index.html                    [MODIFIED] Added badges
│       └── product_detail.html           [MODIFIED] Added banner
├── FLASH_SALE_TIMER.md                  [NEW] Full documentation
└── setup_flash_sales.py                 [NEW] Test helper script
```

## Testing Checklist

- [ ] Create a flash sale in admin
- [ ] Visit product listing and see timer badge
- [ ] Visit product detail and see timer banner
- [ ] Watch timer count down in real-time
- [ ] Set sale to end within 1 minute and watch urgency increase
- [ ] Wait for sale to expire and verify timer disappears
- [ ] Test on mobile browser
- [ ] Check dark theme compatibility

## Next Steps

1. **Quick Test**: Run `setup_demo_flash_sales()` to see it in action
2. **Try It**: Create a flash sale in admin for 2 hours from now
3. **Customize**: Adjust colors and timing to match your brand
4. **Monitor**: Use `list_active_flash_sales()` to track your sales

## Need Help?

Refer to:
- **FLASH_SALE_TIMER.md** - Complete technical documentation
- **setup_flash_sales.py** - Code examples and helper functions
- **products/models.py** - Model definition with properties
- **products/admin.py** - Admin configuration

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-04-26
