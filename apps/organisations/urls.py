from django.urls import path

from .views import (
    OrganisationCreateView,
    OrganisationDetailView,
    OrganisationListView,
    accept_invite,
    invite_member,
    org_leave_view,
)

app_name = "organisations"

urlpatterns = [
    path("", OrganisationListView.as_view(), name="list"),
    path("new/", OrganisationCreateView.as_view(), name="create"),
    path("<slug:slug>/", OrganisationDetailView.as_view(), name="detail"),
    path("<slug:slug>/invite/", invite_member, name="invite"),
    path("<slug:slug>/leave/", org_leave_view, name="leave"),
    path("invite/<str:token>/accept/", accept_invite, name="accept-invite"),
]
