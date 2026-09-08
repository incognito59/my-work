#!/usr/bin/env bash
set -e

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Only load data if no products exist
python manage.py shell -c "
from products.models import Product
if Product.objects.count() == 0:
    print('No products found - loading data.json...')
    from django.core.management import call_command
    call_command('loaddata', 'data.json')
    print('Data loaded successfully!')
else:
    print(f'Products already exist ({Product.objects.count()} found) - skipping loaddata')
"

# Fix site domain
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    id=1,
    defaults={
        'domain': 'retail-logistics-core.onrender.com',
        'name': 'RedCart'
    }
)
print('Site domain updated successfully')
"