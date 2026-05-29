import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywork.settings')
django.setup()

from products.models import Product
from collections import Counter

cats = Counter(Product.objects.values_list('category', flat=True))
for cat, count in sorted(cats.items()):
    print(count, cat)
print('Total:', Product.objects.count())
