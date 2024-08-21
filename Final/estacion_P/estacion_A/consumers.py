import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EstacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Aquí conectamos al canal
        self.group_name = 'estaciones_group'

        # Añadimos este canal al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Aquí desconectamos del canal
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Este método recibe los mensajes del WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Este método recibe los mensajes del grupo y los envía al WebSocket
    async def chat_message(self, event):
        message = event['message']

        # Enviar el mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
