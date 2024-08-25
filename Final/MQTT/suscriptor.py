import paho.mqtt.client as mqtt
import json
import pymysql
from pymysql import OperationalError
from websocket import create_connection

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion_g1/#"
websocket_url = 'ws://itt363-1.smar.com.do/ws/estaciones/'

# Configuración de la base de datos
db_config = {
    'user': 'grupo1',
    'password': 'grupo1',
    'host': '192.168.100.151',
    'database': 'estaciones_meteorologicas'
}

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
            temperatura = datos['temperatura']
            humedad = datos['humedad']
            presion = datos['presion']
            velocidad_viento = datos['velocidad_viento']
            direccion_viento = datos['direccion_viento']
            pluvialidad = datos['pluvialidad']

            # Insertar datos en la base de datos
            insert_data(estacion_id, fecha, temperatura, humedad, presion, velocidad_viento, direccion_viento, pluvialidad)
            
            # Enviar los datos a través de WebSockets
            enviar_a_websocket(estacion_id, fecha, temperatura, humedad, presion, velocidad_viento, direccion_viento, pluvialidad)
        else:
            print(f"El dato para la estación {estacion_id} con fecha {fecha} ya existe en la base de datos.")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el mensaje: {e}")
    except KeyError as e:
        print(f"Clave faltante en el JSON: {e}")

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

# Función para insertar datos en la base de datos
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
    except OperationalError as e:
        print(f"Error al conectar con MySQL: {e}")
    except pymysql.MySQLError as e:
        print(f"Error en la operación de MySQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Función para enviar datos al servidor WebSocket
def enviar_a_websocket(estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad):
    ws_data = {
        "idestacion": estacion_id,
        "fecha": fecha,
        "temperatura": temp,
        "humedad": humedad,
        "presion": presion,
        "velocidad_viento": velocidad,
        "direccion_viento": direccion,
        "pluvialidad": pluvialidad
    }

    try:
        ws = create_connection(websocket_url)
        ws.send(json.dumps(ws_data))
        print(f"Datos enviados al WebSocket: {json.dumps(ws_data)}")
        ws.close()
    except Exception as e:
        print(f"Error al conectar o enviar datos al WebSocket: {e}")

# Configuración del cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
client.connect(broker_address, broker_port)

# Mantener el script en ejecución
client.loop_start()
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Desconectando del broker MQTT...")
    client.disconnect()

