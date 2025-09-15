import json

from channels.generic.websocket import AsyncWebsocketConsumer

class FriendConsumer(AsyncWebsocketConsumer):
     
     async def connect(self):
        self.user = self.scope["user"] # Текущий пользователь

        self.room_name = f"incoming_friends_{self.user.id}" # Создание комнаты

        # Присоединяемся к группе (комнате)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()


     async def disconnect(self, close_code):
         # Покидаем комнату
         await self.channel_layer.group_discard(self.room_name, self.channel_name)


     async def incomming_friends(self, event):
        # Отправляем сообщение на WebSocket
        await self.send(text_data=json.dumps({
            "image": event["image"],
            "sender_id": event["sender_id"],
            "user_name":event["user_name"]
        }))