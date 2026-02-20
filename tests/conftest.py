import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", email="test@example.com", password="password123")


@pytest.fixture
def user_with_leave(user):
    user.annual_leave_allowance = 25
    user.carryover_days = 5
    user.save()
    return user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
