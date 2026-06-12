from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from decouple import config


class Command(BaseCommand):
    help = 'Creates the default Site object for django.contrib.sites'

    def handle(self, *args, **options):
        site_url = config('SITE_URL', default='http://localhost:8000')
        domain = site_url.replace('https://', '').replace('http://', '').rstrip('/')
        site_name = 'Retail Logistics Core'

        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': domain,
                'name': site_name,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created Site: {site.name} ({site.domain})'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Site with ID=1 already exists: {site.name} ({site.domain})'
                )
            )
