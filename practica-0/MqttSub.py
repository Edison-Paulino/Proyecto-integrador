import paho.mqtt.client as mqtt
import json
import mysql.connector
from mysql.connector import Error

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion/#"

# Configuración de la base de datos
db_config = {
    'user' : 'grupo1',
    'password' : 'grupo1',
    'host' : '192.168.100.151',
    'database' : 'estaciones_meteorologicas'
}

def insert_data(estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad):
    conneccion = None
    try:
        conneccion = mysql.connector.connect(**db_config)
        if conneccion.is_connected():
            cursor = conneccion.cursor()
            sql = """INSERT INTO datos_estacion 
                     (IdEstacion, Fecha, Temperatura, Humedad, Presion, Velocidad_Viento, Direccion_Viento, Pluvialidad)  
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (estacion_id, fecha, temp, humedad, presion, velocidad, direccion, pluvialidad))
            conneccion.commit()
            print("Datos insertados correctamente.")
    except Error as e:
        print(f"Error al conectar con MySQL: {e}")
    finally:
        if conneccion is not None and conneccion.is_connected():
            cursor.close()
            conneccion.close()

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
        estacion_id = datos['estacion_id']
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

# Configuración del cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
client.connect(broker_address, broker_port)

# Ejecución del suscriptor
if __name__ == "__main__":
    try:
        print("Suscriptor iniciado. Presiona Ctrl+C para terminar.")
        client.loop_forever()
    except KeyboardInterrupt:
        print("Suscripción terminada.")
        client.disconnect()
