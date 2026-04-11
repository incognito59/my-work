"""
Fix duplicate social auth apps and register them properly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywork.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Check existing social apps
print("Current Social Apps:")
for app in SocialApp.objects.all():
    print(f"  - {app.provider}: {app.name}")

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
print("✅ Google OAuth app registered")

# Create GitHub
github = SocialApp.objects.create(
    provider='github',
    name='GitHub',
    client_id='Ov23lihdNaFu6mZNXuve',
    secret='a193ed7aac260c3768a98fd3b684e739998f65dd'
)
github.sites.add(Site.objects.get_current())
print("✅ GitHub OAuth app registered")

print("\n✅ All social apps fixed!")
print("\nFinal Social Apps:")
for app in SocialApp.objects.all():
    print(f"  - {app.provider}: {app.name}")
