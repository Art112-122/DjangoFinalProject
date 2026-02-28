"""
ASGI config for core project.
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # Исправил опечатку
from django.core.asgi import get_asgi_application  # ops? osgi? нет!
import os
from chat.routing import websocket_urlpatterns  # с точкой!

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})