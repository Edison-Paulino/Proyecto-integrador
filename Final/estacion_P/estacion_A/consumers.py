import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
import asyncio
from .models import Estacion, DatosEstacion  # Cambia estos nombres según tus modelos

class EstacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'estaciones_group'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Recibir mensajes desde WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'enviar_datos_estacion',
                'data': data  # Enviar todos los datos recibidos
            }
        )

    # Enviar datos a los clientes
    async def enviar_datos_estacion(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))


class AlertaEstacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.GROUP_NAME = 'alertas_group'
        await self.channel_layer.group_add(
            self.GROUP_NAME, self.channel_name
        )
        await self.accept()

        # Comenzar tarea periódica para verificar estaciones inactivas
        self.keep_running = True
        self.check_task = asyncio.create_task(self.verificar_estaciones_inactivas())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.GROUP_NAME, self.channel_name
        )
        self.keep_running = False
        self.check_task.cancel()
        await self.check_task

    async def verificar_estaciones_inactivas(self):
        while self.keep_running:
            now = datetime.now()
            two_minutes_ago = now - timedelta(minutes=2)
            await self.check_estaciones()
            await asyncio.sleep(60)

    @database_sync_to_async
    def check_estaciones(self):
        now = datetime.now()
        estaciones = Estacion.objects.all()
        for estacion in estaciones:
            ultima_lectura = DatosEstacion.objects.filter(estacion=estacion).order_by('-fecha').first()
            if ultima_lectura and (now - ultima_lectura.fecha).total_seconds() > 120:
                # Enviar alerta de estación desconectada
                self.enviar_alerta_inactiva(estacion)

    def enviar_alerta_inactiva(self, estacion):
        async_to_sync(self.channel_layer.group_send)(
            self.GROUP_NAME,
            {
                'type': 'alerta_estacion_inactiva',
                'message': f'La estación {estacion.nombre} está inactiva.',
                'id_estacion': estacion.id
            }
        )

    async def alerta_estacion_inactiva(self, event):
        message = event['message']
        id_estacion = event['id_estacion']
        await self.send(text_data=json.dumps({
            'message': message,
            'id_estacion': id_estacion
        }))
