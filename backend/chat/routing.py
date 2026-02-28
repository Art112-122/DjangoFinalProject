from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # Используем напрямую ChatConsumer
    re_path(r"ws/chat/(?P<room_id>[0-9a-f-]+)/$", ChatConsumer.as_asgi()),
]