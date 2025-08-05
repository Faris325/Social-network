from django.urls import re_path
from notifications.consumers import NotificationsConsumer

ws_urlpatterns = [
    re_path(r'ws/notification/', NotificationsConsumer.as_asgi()),
]