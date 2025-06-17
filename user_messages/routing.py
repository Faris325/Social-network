from django.urls import re_path
from user_messages.consumers import ChatConsumer

ws_urlpatterns = [
    re_path(r'ws/chat/(?P<user_id>\d+)/$', ChatConsumer.as_asgi()),
]