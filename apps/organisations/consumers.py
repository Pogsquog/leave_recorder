import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class OrganisationConsumer(WebsocketConsumer):
    def connect(self):
        self.org_slug = self.scope["url_route"]["kwargs"]["org_slug"]
        self.org_group_name = f"org_{self.org_slug}"

        async_to_sync(self.channel_layer.group_add)(self.org_group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.org_group_name, self.channel_name)

    def leave_update(self, event):
        self.send(text_data=json.dumps(event["data"]))
