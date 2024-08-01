import paho.mqtt.client as mqtt
import json
import pymysql
from pymysql import OperationalError
import asyncio
import django
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime

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
        if not message.payload:
            return  # No hacer nada si el mensaje está vacío

        datos = json.loads(message.payload.decode("utf-8"))
        
        # Extraer datos del JSON
        estacion_id = datos['idestacion']
        fecha = datos['fecha']

        # Verificar si el dato ya existe en la base de datos
        if not dato_ya_existe(estacion_id, fecha):
            # Formatear los datos en JSON con indentación
            datos_formateados = json.dumps(datos, indent=4)
            
            # Crear una salida formateada
            salida = f"""
            Datos recibidos del tópico {message.topic}:
            {datos_formateados}
            """
            
            # Imprimir la salida
            print(salida)
            
            temperatura = datos['temperatura']
            humedad = datos['humedad']
            presion = datos['presion']
            velocidad_viento = datos['velocidad_viento']
            direccion_viento = datos['direccion_viento']
            pluvialidad = datos['pluvialidad']

            print("Insertando datos:")
            
            # Insertar datos en la base de datos
            insert_data(estacion_id, fecha, temperatura, humedad, presion, velocidad_viento, direccion_viento, pluvialidad)
        else:
            ## Publicar mensajes vacíos para limpiar los retenidos
            """print(f"El dato para la estación {estacion_id} con fecha {fecha} ya existe en la base de datos.")"""
            topics = ["estacion_g1/101/sensores_g1", "estacion_g1/102/sensores_g1", "estacion_g1/103/sensores_g1", "estacion_g1/104/sensores_g1", "estacion_g1/105/sensores_g1"]
            for topic in topics:
                client.publish(topic, payload=None, retain=True)

    except json.JSONDecodeError as e:
        print(f"Error al decodificar el mensaje: {e}")
    except KeyError as e:
        print(f"Clave faltante en el JSON: {e}")
    except ValueError as e:
        print(f"Error en el formato de fecha: {e}")

# Función para verificar si el dato ya existe en la base de datos
def dato_ya_existe(estacion_id, fecha):
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        sql = "SELECT COUNT(*) FROM datos_estacion WHERE IdEstacion = %s AND Fecha = %s"
        cursor.execute(sql, (estacion_id, fecha))
        result = cursor.fetchone()
        return result[0] > 0
    except OperationalError as e:
        print(f"Error al conectar con MySQL: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

# Función para insertar datos en la base de datos y notificar a través de WebSocket
def insert_data(estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad):
    connection = None
    try:
        connection = pymysql.connect(**db_config)
        if connection:
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
    except OperationalError as e:
        print(f"Error al conectar con MySQL: {e}")
    except pymysql.MySQLError as e:
        print(f"Error en la operación de MySQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Configuración del cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
client.connect(broker_address, broker_port)

# Asegurarse de recibir mensajes retenidos
client.loop_start()

# Mantener el script en ejecución
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Desconectando del broker MQTT...")
    client.disconnect()
