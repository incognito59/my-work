#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata data.json
python manage.py shell -c 'from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={"domain":"retail-logistics-core-t0xz.onrender.com", "name": "RedCart"})'