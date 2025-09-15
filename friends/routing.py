from django.urls import re_path
from friends.consumers import FriendConsumer

ws_urlpatterns = [
    re_path(r'ws/friends/', FriendConsumer.as_asgi()),
]