from django.middleware.csrf import CsrfViewMiddleware


class CsrfExemptMiddleware(CsrfViewMiddleware):
    """CSRF middleware that exempts requests authenticated via API key."""

    def _accept(self, request):
        """Mark request as CSRF exempt."""
        setattr(request, "_csrf_processing_done", True)
        return None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """Skip CSRF check for API key authenticated requests."""
        if hasattr(request, "user") and request.user.is_authenticated:
            api_key = request.META.get("HTTP_X_API_KEY") or request.query_params.get("api_key")
            if api_key:
                return self._accept(request)
        return super().process_view(request, callback, callback_args, callback_kwargs)
