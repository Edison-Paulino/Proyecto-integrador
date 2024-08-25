from django.urls import path
from .consumers import EstacionConsumer, AlertaEstacionConsumer

websocket_urlpatterns = [
    path('ws/estaciones/', EstacionConsumer.as_asgi()),
    path('ws/alertas/', AlertaEstacionConsumer.as_asgi()),
]
