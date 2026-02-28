import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import ChatRoom, Message
from django.contrib.auth import get_user_model
from datetime import datetime

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

            # Добавляем в группу Redis
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            print(f"✅ WebSocket через REDIS подключен: {self.user.username} в комнате {self.room_id}")

            # Уведомляем всех что пользователь онлайн
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "status": "online"
                }
            )

        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'room_group_name') and hasattr(self, 'user'):
                # Уведомляем что пользователь офлайн
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "user_status",
                        "user_id": self.user.id,
                        "username": self.user.username,
                        "status": "offline"
                    }
                )

                # Удаляем из группы Redis
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        except Exception as e:
            print(f"❌ Ошибка при отключении: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type", "message")

            if message_type == "message":
                message = data.get("message", "").strip()

                if not message:
                    return

                if len(message) > 5000:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "error": "Сообщение слишком длинное"
                    }))
                    return

                # Сохраняем в базу
                saved_message = await self.save_message(self.user.id, message)

                # Отправляем через Redis ВСЕМ в комнате
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": saved_message["text"],
                        "user": saved_message["sender__username"],
                        "user_id": saved_message["sender_id"],
                        "created_at": saved_message["created_at"].isoformat() if saved_message["created_at"] else None,
                    }
                )

            elif message_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))

        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_message",
            "message": event["message"],
            "user": event["user"],
            "user_id": event["user_id"],
            "created_at": event["created_at"],
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status_update",
            "user_id": event["user_id"],
            "username": event["username"],
            "status": event["status"],
        }))

    @database_sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.select_related('buyer', 'seller').get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, user_id, text):
        message = Message.objects.create(
            room_id=self.room_id,
            sender_id=user_id,
            text=text
        )
        return {
            "text": message.text,
            "sender_id": message.sender_id,
            "sender__username": message.sender.username,
            "created_at": message.created_at
        }