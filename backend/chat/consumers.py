import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
            self.room_group_name = f"chat_{self.room_id}"

            self.user = self.scope.get("user")
            if not self.user or not self.user.is_authenticated:
                await self.close()
                return

            self.room = await self.get_room()
            if not self.room:
                await self.close()
                return

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            print(
                f"✅ WebSocket через REDIS подключен: {self.user.username} в комнате {self.room_id}"
            )

            await self.mark_messages_as_read()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "status": "online",
                },
            )
        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, "room_group_name") and hasattr(self, "user"):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_status",
                        "user_id": self.user.id,
                        "username": self.user.username,
                        "status": "offline",
                    },
                )

                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )

        except Exception as e:
            print(f"❌ Ошибка при отключении: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                message_text = data.get("message", "").strip()
                if not message_text:
                    return

                saved_message = await self.save_message(self.user.id, message_text)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": saved_message["text"],
                        "user": saved_message["username"],  # Тут должно быть username
                        "user_id": saved_message["sender_id"],
                        "created_at": saved_message["created_at"],
                        "is_read": saved_message["is_read"],
                    },
                )
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_message",
                    "message": event["message"],
                    "user": event["user"],
                    "user_id": event["user_id"],
                    "created_at": event["created_at"],
                    "is_read": event.get("is_read", False),
                }
            )
        )

    async def user_status(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "status_update",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "status": event["status"],
                }
            )
        )

    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(room_id=self.room_id, is_read=False).exclude(
            sender=self.user
        ).update(is_read=True)

    @database_sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.select_related("buyer", "seller").get(
                id=self.room_id
            )
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, user_id, text):
        message = Message.objects.create(
            room_id=self.room_id,
            sender_id=user_id,
            text=text,
            is_read=False,  # Не забудь про поле непрочитанных
        )
        return {
            "text": message.text,
            "sender_id": message.sender_id,
            "username": message.sender.username,  # Поменяли ключ на username
            "created_at": message.created_at.isoformat(),  # Сразу в строку
            "is_read": message.is_read,
        }
