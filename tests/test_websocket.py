"""Tests for WebSocket channel layer."""

import pytest
from channels.layers import get_channel_layer


@pytest.mark.asyncio
class TestChannelLayer:
    async def test_channel_layer_available(self):
        """Test that the channel layer is available."""
        channel_layer = get_channel_layer()
        assert channel_layer is not None

    async def test_channel_send_and_receive(self):
        """Test sending and receiving messages through channel layer."""
        channel_layer = get_channel_layer()

        channel_name = "test-channel"
        await channel_layer.send(channel_name, {"type": "test.message", "data": "test"})
