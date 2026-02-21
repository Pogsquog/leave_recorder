"""URL configuration for holiday_holliday project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core import views as core_views

urlpatterns = [
    path("healthz", core_views.healthz, name="healthz"),
    path("ready", core_views.ready, name="ready"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("apps.api.urls")),
    path("", include("apps.leave.urls")),
    path("account/", include("apps.users.urls", namespace="account")),
    path("org/", include("apps.organisations.urls")),
]
