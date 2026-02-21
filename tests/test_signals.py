"""Tests for signal handlers."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from apps.leave.models import LeaveEntry, LeaveType
from apps.organisations.models import Organisation, OrganisationMembership, OrganisationRole

User = get_user_model()


@pytest.mark.django_db
class TestLeaveEntrySignals:
    def test_leave_entry_created_signal(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        mock_send = MagicMock()
        with patch("apps.organisations.signals.async_to_sync", return_value=mock_send):
            LeaveEntry.objects.create(
                user=user,
                date=date.today(),
                leave_type=LeaveType.VACATION,
                half_day=False,
            )

            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][1]["type"] == "leave_update"
            assert call_args[0][1]["data"]["action"] == "created"
            assert call_args[0][1]["data"]["user_id"] == user.id

    def test_leave_entry_updated_signal(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        LeaveEntry.objects.create(
            user=user,
            date=date.today(),
            leave_type=LeaveType.VACATION,
            half_day=False,
        )

        mock_send = MagicMock()
        with patch("apps.organisations.signals.async_to_sync", return_value=mock_send):
            entry = LeaveEntry.objects.get(user=user, date=date.today())
            entry.half_day = True
            entry.save()

            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][1]["type"] == "leave_update"
            assert call_args[0][1]["data"]["action"] == "updated"

    def test_leave_entry_deleted_signal(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        entry = LeaveEntry.objects.create(
            user=user,
            date=date.today(),
            leave_type=LeaveType.VACATION,
            half_day=False,
        )

        mock_send = MagicMock()
        with patch("apps.organisations.signals.async_to_sync", return_value=mock_send):
            entry.delete()

            assert mock_send.called
            call_args = mock_send.call_args
            assert call_args[0][1]["type"] == "leave_update"
            assert call_args[0][1]["data"]["action"] == "deleted"

    def test_signal_fails_silently_when_channel_layer_none(self, user):
        with patch("apps.organisations.signals.async_to_sync") as mock_async_to_sync:
            mock_async_to_sync.side_effect = Exception("Channel layer error")

            entry = LeaveEntry.objects.create(
                user=user,
                date=date.today(),
                leave_type=LeaveType.VACATION,
                half_day=False,
            )

            assert entry.id is not None

    def test_signal_message_format(self, user):
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        OrganisationMembership.objects.create(organisation=org, user=user, role=OrganisationRole.MEMBER)

        mock_send = MagicMock()
        with patch("apps.organisations.signals.async_to_sync", return_value=mock_send):
            LeaveEntry.objects.create(
                user=user,
                date=date(2026, 1, 15),
                leave_type=LeaveType.SICK,
                half_day=True,
            )

            call_args = mock_send.call_args
            data = call_args[0][1]["data"]
            assert data["date"] == "2026-01-15"
            assert data["leave_type"] == "sick"
            assert data["half_day"] is True
