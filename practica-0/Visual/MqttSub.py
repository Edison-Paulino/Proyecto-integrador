import paho.mqtt.client as mqtt
import json
import mysql.connector
from mysql.connector import Error
import asyncio
import django
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion_g1/#"

# Configuración de la base de datos
db_config = {
    'user': 'grupo1',
    'password': 'grupo1',
    'host': '192.168.100.151',
    'database': 'estaciones_meteorologicas'
}

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visual.settings')
django.setup()

# Callback cuando se conecta al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT con éxito")
        client.subscribe(topic_root)  # Suscríbete al tópico raíz
    else:
        print(f"Error al conectar, código de error: {rc}")

# Callback cuando se recibe un mensaje
def on_message(client, userdata, message):
    try:
        datos = json.loads(message.payload.decode("utf-8"))
        print(f"Datos recibidos del tópico {message.topic}: {datos}")

        # Extraer datos del JSON
        estacion_id = datos['idestacion']
        fecha = datos['fecha']
        temperatura = datos['temperatura']
        humedad = datos['humedad']
        presion = datos['presion']
        velocidad_viento = datos['velocidad_viento']
        direccion_viento = datos['direccion_viento']
        pluvialidad = datos['pluvialidad']
        
        # Insertar datos en la base de datos
        insert_data(estacion_id, fecha, temperatura, humedad, presion, velocidad_viento, direccion_viento, pluvialidad)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el mensaje: {e}")
    except KeyError as e:
        print(f"Clave faltante en el JSON: {e}")

# Función para insertar datos en la base de datos y notificar a través de WebSocket
def insert_data(estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad):
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            sql = """INSERT INTO datos_estacion 
                     (IdEstacion, Fecha, Temperatura, Humedad, Presion, Velocidad_Viento, Direccion_Viento, Pluvialidad)  
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad))
            connection.commit()
            print("Datos insertados correctamente.")
            
            # Datos para notificación WebSocket
            data = {
                'estacion_id': estacion_id,
                'fecha': fecha,
                'temperatura': temp,
                'humedad': humedad,
                'presion': presion,
                'velocidad_viento': velocidad,
                'direccion_viento': direccion,
                'pluvialidad': pluvialidad
            }

            # Notificar a través de WebSockets
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'datos_estacion',
                {
                    'type': 'send_datos',
                    'data': data,
                }
            )
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Configuración del cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
client.connect(broker_address, broker_port)

# Ejecutar el bucle de MQTT en un hilo separado
client.loop_start()

# Mantener el script en ejecución
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Desconectando del broker MQTT...")
    client.disconnect()
