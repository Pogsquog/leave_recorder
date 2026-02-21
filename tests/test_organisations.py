"""Tests for organisation models and views."""

from datetime import datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.organisations.models import Invite, Organisation, OrganisationMembership, OrganisationRole

User = get_user_model()


@pytest.mark.django_db
class TestOrganisation:
    def test_create_organisation(self):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert str(org) == "Test Org"

    def test_organisation_slug_unique(self):
        Organisation.objects.create(name="Test Org", slug="test-org")
        with pytest.raises(Exception):  # noqa: B017
            Organisation.objects.create(name="Another Org", slug="test-org")

    def test_get_members_leave_entries(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        from apps.leave.models import LeaveEntry

        entry = LeaveEntry.objects.create(user=user, date="2026-01-15")

        entries = org.get_members_leave_entries()
        assert entry in entries

    def test_get_members_leave_entries_with_date_filter(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        from apps.leave.models import LeaveEntry

        entry1 = LeaveEntry.objects.create(user=user, date="2026-01-15")
        entry2 = LeaveEntry.objects.create(user=user, date="2026-02-15")

        start_date = datetime(2026, 1, 1).date()
        end_date = datetime(2026, 1, 31).date()

        entries = org.get_members_leave_entries(start_date=start_date, end_date=end_date)
        assert entry1 in entries
        assert entry2 not in entries


@pytest.mark.django_db
class TestOrganisationMembership:
    def test_create_membership(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        membership = OrganisationMembership.objects.create(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )
        assert membership.role == OrganisationRole.MEMBER
        assert str(membership) == "testuser @ Test Org"

    def test_admin_role(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        membership = OrganisationMembership.objects.create(
            organisation=org,
            user=user,
            role=OrganisationRole.ADMIN,
        )
        assert membership.role == OrganisationRole.ADMIN

    def test_unique_membership(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)
        with pytest.raises(Exception):  # noqa: B017
            OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.ADMIN)


@pytest.mark.django_db
class TestInvite:
    def test_create_invite(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        invite = Invite.objects.create(
            organisation=org,
            email="newuser@example.com",
            invited_by=user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert invite.email == "newuser@example.com"
        assert invite.token is not None
        assert len(invite.token) > 0
        assert str(invite) == "Invite to Test Org for newuser@example.com"

    def test_invite_is_expired(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        expired_invite = Invite.objects.create(
            organisation=org,
            email="expired@example.com",
            invited_by=user,
            expires_at=timezone.now() - timedelta(days=1),
        )
        active_invite = Invite.objects.create(
            organisation=org,
            email="active@example.com",
            invited_by=user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert expired_invite.is_expired is True
        assert active_invite.is_expired is False

    def test_invite_is_accepted(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        invite = Invite.objects.create(
            organisation=org,
            email="accepted@example.com",
            invited_by=user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert invite.is_accepted is False

        invite.accepted_at = timezone.now()
        invite.save()
        assert invite.is_accepted is True

    def test_accept_invite(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        new_user = User.objects.create_user(username="newuser", email="newuser@example.com", password="password123")
        invite = Invite.objects.create(
            organisation=org,
            email="newuser@example.com",
            invited_by=user,
            expires_at=timezone.now() + timedelta(days=7),
        )

        invite.accept(new_user)

        assert invite.is_accepted is True
        assert OrganisationMembership.objects.filter(organisation=org, user=new_user).exists()
        membership = OrganisationMembership.objects.get(organisation=org, user=new_user)
        assert membership.role == OrganisationRole.MEMBER

    def test_accept_expired_invite(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        new_user = User.objects.create_user(username="newuser2", email="newuser2@example.com", password="password123")
        invite = Invite.objects.create(
            organisation=org,
            email="newuser2@example.com",
            invited_by=user,
            expires_at=timezone.now() - timedelta(days=1),
        )

        invite.accept(new_user)

        assert OrganisationMembership.objects.filter(organisation=org, user=new_user).exists()


@pytest.mark.django_db
class TestOrganisationViews:
    def test_organisation_list_view(self, client, user):
        Organisation.objects.create(name="Test Org", slug="test-org")
        client.force_login(user)
        response = client.get("/org/")
        assert response.status_code == 200

    def test_organisation_detail_view(self, client, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)
        client.force_login(user)
        response = client.get(f"/org/{org.slug}/")
        assert response.status_code == 200

    def test_organisation_create_view(self, client, user):
        client.force_login(user)
        response = client.post("/org/create/", {"name": "New Org", "slug": "new-org"})
        assert response.status_code == 302
        assert Organisation.objects.filter(slug="new-org").exists()

    def test_organisation_invite_view(self, client, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.ADMIN)
        client.force_login(user)
        response = client.post(f"/org/{org.slug}/invite/", {"email": "invite@example.com"})
        assert response.status_code == 302
        assert Invite.objects.filter(email="invite@example.com", organisation=org).exists()
