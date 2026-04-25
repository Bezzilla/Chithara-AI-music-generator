from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class ChitharaAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        if not sociallogin.email_addresses:
            return
        from allauth.account.models import EmailAddress
        email = sociallogin.email_addresses[0].email
        try:
            existing = EmailAddress.objects.get(email__iexact=email)
            sociallogin.connect(request, existing.user)
        except EmailAddress.DoesNotExist:
            pass
