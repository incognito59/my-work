import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywork.settings')
django.setup()

from products.models import Product

# ============ CATEGORY FIXES ============
category_fixes = {
    2575: 'Sneakers',        # New Balance 990v6
    2582: 'Sneakers',        # Louis Vuitton Trainer
    2672: 'Sneakers',        # New Balance 574
    2702: 'Electronics',     # Ring Video Doorbell Pro 2
    2706: 'Home Appliances', # Vitamix 5200 Blender
    2619: 'Fitness',         # Nike Pro Training Shorts
    2620: 'Fitness',         # Under Armour Hoodie
}

# ============ STRUCTURALLY CLEAN, UNIQUE IMAGE ADDRESSES ============
# Every address below uses a custom base hash string to completely prevent code-breaking parameters
image_fixes = {
    # Electronics
    2548: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2549: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2565: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2623: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2624: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2625: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2626: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2627: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2628: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2629: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2630: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2631: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2632: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2633: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2634: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2635: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2636: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2637: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2691: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2692: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2693: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2699: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2700: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2701: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2703: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ),
    2704: (
        'https://unsplash.com',
        'https://unsplash.com',
        'https://unsplash.com'
    ), 
}

# ============ RUN DATABASE UPDATE ============
updated_count = 0

for pid, urls in image_fixes.items():
    try:
        product = Product.objects.get(id=pid)
        
        if pid in category_fixes:
            product.category = category_fixes[pid]
            
        # Write clean raw URL text directly to database properties
        product.image_url = urls[0] if len(urls) > 0 else ""
        if hasattr(product, 'image_2') and len(urls) > 1:
            product.image_2 = urls[1]
        if hasattr(product, 'image_3') and len(urls) > 2:
            product.image_3 = urls[2]
            
        product.save()
        updated_count += 1
    except Product.DoesNotExist:
        print(f"Warning: Product ID {pid} not found.")
print(f"Successfully processed {updated_count} clean database updates.")