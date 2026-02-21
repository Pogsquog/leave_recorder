"""Integration tests for full API workflows."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.api.models import APIKey
from apps.leave.models import LeaveEntry, LeaveType
from apps.organisations.models import Invite, Organisation, OrganisationMembership, OrganisationRole

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationWorkflow:
    """Test full user registration to leave creation workflow."""

    def test_user_registration_to_leave_creation(self, client):
        """Test: Register -> Create leave -> View stats."""
        response = client.post(
            "/account/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "password123",
                "password2": "password123",
            },
        )
        assert response.status_code == 302

        user = User.objects.get(username="newuser")
        client.force_login(user)

        response = client.post(
            "/leave/add/",
            {
                "date": "2026-01-15",
                "leave_type": "vacation",
                "half_day": False,
            },
        )
        assert response.status_code == 302
        assert LeaveEntry.objects.filter(user=user, date="2026-01-15").exists()

        response = client.get("/leave/")
        assert response.status_code == 200
        assert "year_stats" in response.context

    def test_user_profile_update(self, client, user):
        """Test: Login -> Update profile -> Verify changes."""
        client.force_login(user)

        response = client.post(
            "/account/preferences/",
            {
                "week_start": 0,
                "annual_leave_allowance": 30,
            },
        )
        assert response.status_code == 302

        user.refresh_from_db()
        assert user.week_start == 0
        assert user.annual_leave_allowance == 30


@pytest.mark.django_db
class TestOrganisationInviteWorkflow:
    """Test organisation invite and acceptance workflow."""

    def test_invite_to_accepted_member(self, client, user):
        """Test: Create org -> Invite user -> Accept invite -> View shared leave."""
        client.force_login(user)

        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.ADMIN)

        response = client.post(
            f"/org/{org.slug}/invite/",
            {"email": "invitee@example.com"},
        )
        assert response.status_code == 302
        assert Invite.objects.filter(email="invitee@example.com", organisation=org).exists()

        invite = Invite.objects.get(email="invitee@example.com", organisation=org)
        invitee = User.objects.create_user(
            username="invitee",
            email="invitee@example.com",
            password="password123",
        )

        invite.accept(invitee)

        client.force_login(invitee)
        response = client.get(f"/org/{org.slug}/")
        assert response.status_code == 200

    def test_org_member_leave_visibility(self, user):
        """Test organisation members can see each other's leave."""
        org = Organisation.objects.create(name="Test Org", slug="test-org")

        user1 = user
        OrganisationMembership.objects.create(organisation=org, user=user1, role=OrganisationRole.MEMBER)

        user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")
        OrganisationMembership.objects.create(organisation=org, user=user2, role=OrganisationRole.MEMBER)

        entry1 = LeaveEntry.objects.create(
            user=user1,
            date=date(2026, 1, 15),
            leave_type=LeaveType.VACATION,
        )

        entries = org.get_members_leave_entries()
        assert entry1 in entries


@pytest.mark.django_db
class TestAPIKeyWorkflow:
    """Test API key creation and authenticated requests."""

    def test_api_key_creation_and_usage(self, api_client, user):
        """Test: Create API key -> Use key for authenticated requests."""
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/api-keys/",
            {"name": "Test Key"},
        )
        assert response.status_code == 201
        assert "key" in response.data
        assert "warning" in response.data

        key_id = response.data["id"]
        api_key = APIKey.objects.get(id=key_id)
        assert api_key.name == "Test Key"

    def test_api_key_list(self, api_client, user):
        """Test listing API keys."""
        api_client.force_authenticate(user=user)

        APIKey.objects.create(user=user, name="Key 1")
        APIKey.objects.create(user=user, name="Key 2")

        response = api_client.get("/api/api-keys/")
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_api_key_delete(self, api_client, user):
        """Test deleting an API key."""
        api_client.force_authenticate(user=user)

        key = APIKey.objects.create(user=user, name="To Delete")

        response = api_client.delete(
            "/api/api-keys/",
            {"id": key.id},
        )
        assert response.status_code == 204
        assert not APIKey.objects.filter(id=key.id).exists()

    def test_leave_entry_via_api(self, api_client, user):
        """Test creating leave entry via API."""
        api_client.force_authenticate(user=user)

        response = api_client.post(
            "/api/leave-entries/",
            {
                "date": "2026-02-15",
                "leave_type": "vacation",
                "half_day": False,
                "notes": "API created",
            },
        )
        assert response.status_code == 201
        assert LeaveEntry.objects.filter(user=user, date="2026-02-15").exists()

    def test_leave_entries_list_via_api(self, api_client, user):
        """Test listing leave entries via API."""
        api_client.force_authenticate(user=user)

        LeaveEntry.objects.create(user=user, date="2026-01-15", leave_type=LeaveType.VACATION)
        LeaveEntry.objects.create(user=user, date="2026-02-15", leave_type=LeaveType.SICK)

        response = api_client.get("/api/leave-entries/")
        assert response.status_code == 200
        assert len(response.data) > 0

    def test_leave_stats_via_api(self, api_client, user_with_leave):
        """Test getting leave stats via API."""
        api_client.force_authenticate(user=user_with_leave)

        LeaveEntry.objects.create(
            user=user_with_leave,
            date="2026-01-15",
            leave_type=LeaveType.VACATION,
        )

        response = api_client.get("/api/leave-entries/stats/")
        assert response.status_code == 200
        assert "total_allowance" in response.data
        assert "taken_days" in response.data
        assert "remaining_days" in response.data


@pytest.mark.django_db
class TestOrganisationAPIWorkflow:
    """Test organisation API endpoints."""

    def test_list_organisations_via_api(self, api_client, user):
        """Test listing organisations via API."""
        api_client.force_authenticate(user=user)

        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        response = api_client.get("/api/organisations/")
        assert response.status_code == 200
        assert len(response.data) > 0

    def test_organisation_members_via_api(self, api_client, user):
        """Test getting organisation members via API."""
        api_client.force_authenticate(user=user)

        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.ADMIN)

        user2 = User.objects.create_user(username="member2", email="member2@example.com", password="password123")
        OrganisationMembership.objects.create(organisation=org, user=user2, role=OrganisationRole.MEMBER)

        response = api_client.get(f"/api/organisations/{org.id}/members/")
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_organisation_leave_entries_via_api(self, api_client, user):
        """Test getting organisation leave entries via API."""
        api_client.force_authenticate(user=user)

        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        LeaveEntry.objects.create(user=user, date="2026-01-15", leave_type=LeaveType.VACATION)

        response = api_client.get(f"/api/organisations/{org.id}/leave-entries/")
        assert response.status_code == 200
        assert len(response.data) > 0


@pytest.mark.django_db
class TestCurrentUserAPIWorkflow:
    """Test current user API endpoint."""

    def test_get_current_user(self, api_client, user):
        """Test getting current user profile."""
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/current-user/")
        assert response.status_code == 200
        assert response.data["username"] == user.username
        assert response.data["email"] == user.email

    def test_update_current_user(self, api_client, user):
        """Test updating current user profile."""
        api_client.force_authenticate(user=user)

        response = api_client.patch(
            "/api/current-user/",
            {
                "week_start": 0,
                "annual_leave_allowance": 28,
            },
        )
        assert response.status_code == 200
        assert response.data["week_start"] == 0
        assert response.data["annual_leave_allowance"] == 28
