import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from .models import SupportRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_id = self.scope['url_route']['kwargs']['room_uuid']
        self.room_group_name = f"chat_{self.room_id}"

        # If the user is not authenticated, close the connection
        if not self.user.is_authenticated:
            await self.close()

        # Join the WebSocket group based on the room UUID
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Fetch previous messages
        messages = await self.get_previous_messages(self.room_id)

        # Send all previous messages to the client
        await self.send(text_data=json.dumps({
            'type': 'previous_messages',
            'messages': messages
        }))

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')

        # If the user is not authenticated, don't save the message
        if not self.user.is_authenticated:
            return

        # Get the support room and save the message to the database
        room = await self.get_room(self.room_id)  # Changed to async call
        new_message = await sync_to_async(Message.objects.create)(
            content=message_content,
            sender=self.user,
            chat=room,
            timestamp=now()
        )

        message_data = {
            'type': 'chat_message',
            'message': new_message.content,
            'sender': new_message.sender.username,
            'timestamp': new_message.timestamp.isoformat()
        }

        # Send the message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    async def chat_message(self, event):
        # Send the message to the user
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_room(self, room_id):
        """ Fetch the support room """
        try:
            return SupportRoom.objects.get(uuid=room_id)
        except SupportRoom.DoesNotExist:
            return None

    @sync_to_async
    def get_previous_messages(self, room_id):
        """ Fetch all messages for the given support room """
        try:
            room = SupportRoom.objects.get(uuid=room_id)
            messages = room.messages.all().order_by('timestamp')
            return [{'message': msg.content, 'sender': msg.sender.username, 'timestamp': msg.timestamp.isoformat()} for msg in messages]
        except SupportRoom.DoesNotExist:
            return []
