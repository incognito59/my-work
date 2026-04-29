from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User

class NoSignupFormAdapter(DefaultSocialAccountAdapter):

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def is_open_for_signup(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        # If a user with this email already exists,
        # connect the Google account to it automatically
        if sociallogin.is_existing:
            return
        try:
            email = sociallogin.user.email
            if email:
                existing_user = User.objects.get(email__iexact=email)
                sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass