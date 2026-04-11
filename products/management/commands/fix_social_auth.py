import os
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Fix duplicate social auth apps and register them properly'

    def handle(self, *args, **options):
        # Remove duplicates
        SocialApp.objects.filter(provider__in=['google', 'github']).delete()

        # Create Google
        google = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
            secret=os.environ.get('GOOGLE_OAUTH_SECRET')
        )
        google.sites.add(Site.objects.get_current())
        self.stdout.write(self.style.SUCCESS('✅ Google OAuth app registered'))

        # Create GitHub
        github = SocialApp.objects.create(
            provider='github',
            name='GitHub',
            client_id='Ov23lihdNaFu6mZNXuve',
            secret='a193ed7aac260c3768a98fd3b684e739998f65dd'
        )
        github.sites.add(Site.objects.get_current())
        self.stdout.write(self.style.SUCCESS('✅ GitHub OAuth app registered'))

        self.stdout.write(self.style.SUCCESS('\n✅ All social apps fixed!'))
        self.stdout.write(self.style.SUCCESS('\nFinal Social Apps:'))
        for app in SocialApp.objects.all():
            self.stdout.write(f'  - {app.provider}: {app.name}')
