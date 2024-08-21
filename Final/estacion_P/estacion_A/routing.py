from django.urls import path
from . import consumers  # Asegúrate de crear el archivo consumers.py para manejar WebSockets

websocket_urlpatterns = [
    path('ws/estaciones/', consumers.EstacionConsumer.as_asgi()),
]
