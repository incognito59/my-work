from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.sites.models import Site
from decouple import config


@receiver(post_migrate)
def create_default_site(sender, **kwargs):
    """Create the default Site object after migrations."""
    if sender.name == 'django.contrib.sites':
        site_url = config('SITE_URL', default='http://localhost:8000')
        domain = site_url.replace('https://', '').replace('http://', '').rstrip('/')
        site_name = 'Retail Logistics Core'

        Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': domain,
                'name': site_name,
            }
        )
