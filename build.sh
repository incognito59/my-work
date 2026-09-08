#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Only load product records if no products exist. The full historical fixture
# contains models that are no longer installed, so loaddata data.json cannot
# be used safely during deployment.
python manage.py shell -c "
import json
from pathlib import Path
from django.core import serializers
from products.models import Product
if Product.objects.count() == 0:
    fixture = json.loads(Path('data.json').read_text(encoding='utf-8'))
    product_records = [item for item in fixture if item.get('model') == 'products.product']
    for product in serializers.deserialize('json', json.dumps(product_records)):
        product.save()
    print(f'Loaded {len(product_records)} products from data.json')
else:
    print(f'Products already exist ({Product.objects.count()} found) - skipping loaddata')
"

# Fix site domain
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    id=1,
    defaults={
        'domain': 'retail-logistics-core-t0xz.onrender.com',
        'name': 'RedCart'
    }
)
print('Site domain updated successfully')
"