from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeaveEntryViewSet, OrganisationViewSet, api_keys, current_user

router = DefaultRouter()
router.register(r"leave", LeaveEntryViewSet, basename="leave")
router.register(r"organisations", OrganisationViewSet, basename="organisations")

urlpatterns = [
    path("", include(router.urls)),
    path("user/", current_user, name="current-user"),
    path("keys/", api_keys, name="api-keys"),
]
