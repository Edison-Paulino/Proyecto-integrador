import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DatoEstacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("datos_estacion", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("datos_estacion", self.channel_name)

    async def send_datos(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))
