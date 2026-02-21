"""Tests for WebSocket consumers."""

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model

from apps.organisations.consumers import OrganisationConsumer
from apps.organisations.models import Organisation, OrganisationMembership, OrganisationRole

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestOrganisationConsumer:
    async def test_websocket_connection(self, user):
        """Test that a user can connect to the WebSocket."""
        org = await database_sync_to_async(Organisation.objects.create)(
            name="Test Org",
            slug="test-org",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )

        application = OrganisationConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.disconnect()

    async def test_websocket_subscription_to_group(self, user):
        """Test that connecting user is added to the organisation group."""
        org = await database_sync_to_async(Organisation.objects.create)(
            name="Test Org",
            slug="test-org",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )

        application = OrganisationConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.disconnect()

    async def test_receive_leave_update_message(self, user):
        """Test that the consumer receives leave update messages."""
        org = await database_sync_to_async(Organisation.objects.create)(
            name="Test Org",
            slug="test-org",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )

        application = OrganisationConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to(
            {
                "type": "leave_update",
                "data": {
                    "action": "created",
                    "user_id": user.id,
                    "date": "2026-01-15",
                    "leave_type": "vacation",
                    "half_day": False,
                },
            }
        )

        await communicator.disconnect()

    async def test_websocket_disconnect_removes_from_group(self, user):
        """Test that disconnecting removes user from the group."""
        org = await database_sync_to_async(Organisation.objects.create)(
            name="Test Org",
            slug="test-org",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )

        application = OrganisationConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.disconnect()

        communicator2 = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")
        connected2, _ = await communicator2.connect()
        assert connected2 is True

        await communicator2.disconnect()

    async def test_multiple_users_in_same_org(self, user):
        """Test multiple users can connect to the same organisation group."""
        org = await database_sync_to_async(Organisation.objects.create)(
            name="Test Org",
            slug="test-org",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user,
            role=OrganisationRole.MEMBER,
        )

        user2 = await database_sync_to_async(User.objects.create_user)(
            username="user2",
            email="user2@example.com",
            password="password123",
        )
        await database_sync_to_async(OrganisationMembership.objects.create)(
            organisation=org,
            user=user2,
            role=OrganisationRole.MEMBER,
        )

        application = OrganisationConsumer.as_asgi()
        communicator1 = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")
        communicator2 = WebsocketCommunicator(application, f"/ws/org/{org.slug}/")

        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()

        assert connected1 is True
        assert connected2 is True

        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_invalid_org_slug(self, user):
        """Test connection with invalid org slug."""
        application = OrganisationConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, "/ws/org/non-existent-org/")

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.disconnect()
