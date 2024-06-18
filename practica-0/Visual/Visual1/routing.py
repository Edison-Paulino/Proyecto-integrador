from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/datos/', consumers.DatosConsumer.as_asgi()),
]
