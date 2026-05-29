import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywork.settings')
django.setup()

from products.models import Product

categories = Product.objects.values_list('category', flat=True).distinct()
for cat in sorted(categories):
    print(f"\n=== {cat} ===")
    products = Product.objects.filter(category=cat)
    for p in products:
        print(f"  {p.id}: {p.name}")