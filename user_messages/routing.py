from django.urls import path
from user_messages.consumers import ChatConsumer

#Лучше использовать path
ws_urlpatterns = [
    path('ws/chat/<int:user_id>/', ChatConsumer.as_asgi()),
]