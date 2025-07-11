import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Messages

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"] # Текущий пользователь

        # Приводим user_id из URL к int
        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id']) # Извлечение из url user_id 

        # Формируем имя комнаты независимо от порядка id
        self.room_name = self.get_room_name(self.user.id, self.other_user_id) # Создание комнаты

        # Присоединяемся к группе (комнате)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем комнату
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):    # Этот метод вызывается, когда клиент отправляет данные по веб соккету 
        data = json.loads(text_data) # Превращение байтовой js строки в словарь 
        message_text = data.get("message") # Извлечение значения из словаря 

        if not message_text:
            return  # Если сообщение пустое, ничего не делаем

        recipient = await self.get_user(self.other_user_id) # Получение объекта пользователя(собеседника)

        # Создаем сообщение в БД
        await self.create_message(self.user, recipient, message_text) # Сохранение записи в бд

        # Отправляем сообщение всем участникам комнаты
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender_id": self.user.id,
                "sender_username": self.user.username,
            }
        )

    async def chat_message(self, event):
        # Отправляем сообщение на WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_username": event["sender_username"],
        }))

    @staticmethod
    def get_room_name(user1_id, user2_id):
        # Чтобы имя комнаты было одинаковым для пары пользователей независимо от порядка
        return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def create_message(self, sender, recipient, message_text):
        return Messages.objects.create(sender=sender, recipient=recipient, content=message_text,)
