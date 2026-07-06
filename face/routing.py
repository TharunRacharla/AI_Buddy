from django.urls import re_path
from face import consumers

websocket_urlpatterns = [
    re_path(r'ws/agent/$', consumers.ChatConsumer.as_asgi()),
]