from rest_framework import authentication, exceptions

from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        key = request.META.get("HTTP_X_API_KEY") or request.query_params.get("api_key")

        if not key:
            return None

        try:
            api_key = APIKey.objects.select_related("user").get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key") from None

        from django.utils import timezone

        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at"])

        return (api_key.user, None)
