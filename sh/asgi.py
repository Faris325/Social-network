"""
ASGI config for sh project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter

from user_messages.routing import ws_urlpatterns as ws_messages
from notifications.routing import ws_urlpatterns as ws_notifiacations
from friends.routing import ws_urlpatterns as ws_incomming_friends

ws_urlpatterns = ws_messages+ws_notifiacations+ws_incomming_friends

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sh.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(ws_urlpatterns)
    )
})
