import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.api.models import APIKey
from apps.leave.models import LeaveEntry, LeaveType

User = get_user_model()


@pytest.mark.django_db
class TestAPIAuthentication:
    def test_no_auth(self):
        client = APIClient()
        response = client.get("/api/leave/")
        assert response.status_code == 403

    def test_api_key_auth(self, user):
        api_key = APIKey.objects.create(user=user)
        client = APIClient()
        response = client.get("/api/leave/", HTTP_X_API_KEY=api_key.key)
        assert response.status_code == 200

    def test_invalid_api_key(self):
        client = APIClient()
        response = client.get("/api/leave/", HTTP_X_API_KEY="invalid-key")
        assert response.status_code == 403


@pytest.mark.django_db
class TestLeaveAPI:
    def test_list_leave_entries(self, authenticated_client, user):
        from datetime import date

        LeaveEntry.objects.create(user=user, date=date.today(), leave_type=LeaveType.VACATION)
        response = authenticated_client.get("/api/leave/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

    def test_create_leave_entry(self, authenticated_client):
        from datetime import date

        data = {
            "date": date.today().isoformat(),
            "leave_type": LeaveType.VACATION,
            "half_day": False,
        }
        response = authenticated_client.post("/api/leave/", data)
        assert response.status_code == 201

    def test_leave_stats(self, authenticated_client, user):
        from datetime import date

        LeaveEntry.objects.create(user=user, date=date.today(), leave_type=LeaveType.VACATION)
        response = authenticated_client.get("/api/leave/stats/")
        assert response.status_code == 200
        assert "total_allowance" in response.data
        assert "taken_days" in response.data


@pytest.mark.django_db
class TestUserAPI:
    def test_get_current_user(self, authenticated_client, user):
        response = authenticated_client.get("/api/user/")
        assert response.status_code == 200
        assert response.data["username"] == user.username

    def test_update_preferences(self, authenticated_client):
        data = {"annual_leave_allowance": 30}
        response = authenticated_client.patch("/api/user/", data)
        assert response.status_code == 200
        assert response.data["annual_leave_allowance"] == 30


@pytest.mark.django_db
class TestAPIKeyManagement:
    def test_list_keys(self, authenticated_client, user):
        APIKey.objects.create(user=user, name="Test Key")
        response = authenticated_client.get("/api/keys/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_create_key(self, authenticated_client):
        response = authenticated_client.post("/api/keys/", {"name": "New Key"})
        assert response.status_code == 201
        assert "key" in response.data

    def test_delete_key(self, authenticated_client, user):
        key = APIKey.objects.create(user=user)
        response = authenticated_client.delete("/api/keys/", {"id": key.id})
        assert response.status_code == 204
