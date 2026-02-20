from django.urls import path

from .consumers import OrganisationConsumer

websocket_urlpatterns = [
    path("ws/org/<slug:org_slug>/", OrganisationConsumer.as_asgi()),
]
