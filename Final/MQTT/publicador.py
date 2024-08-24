import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion_g1/"
topic_root2 = "/sensores_g1"

# Configuración del cliente MQTT
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(broker_address, broker_port)

# Función para generar datos aleatorios
def generar_datos(maquina_id):
    datos = {
        "idestacion": maquina_id,
        "fecha": datetime.now().isoformat(),  # Formato de fecha ISO 8601
        "temperatura": round(random.uniform(20.0, 40), 2),
        "humedad": round(random.uniform(50, 100), 2),
        "presion": round(random.uniform(1000, 1020), 2),
        "velocidad_viento": round(random.uniform(0, 70), 2),
        "direccion_viento": round(random.uniform(0, 360), 2),
        "pluvialidad": round(random.uniform(3, 5), 2)
    }
    return datos

# Publicación de datos
def publicar_datos(espera=3, qos=1, retain=False):  # Intervalo configurable, QoS y Retain configurables
    num_maquinas = 5
    while True:
        for maquina_id in range(101, 101 + num_maquinas):
            datos = generar_datos(maquina_id)
            topic = topic_root + str(maquina_id) + topic_root2
            try:
                # Publicar con el QoS y Retain configurables
                client.publish(topic, json.dumps(datos), qos=qos, retain=retain)
                print(f"Publicado en {topic} con QoS {qos}, Retain {retain}: {datos}")
            except Exception as e:
                print(f"Error al publicar en el tópico {topic}: {e}")
        time.sleep(espera)  # Espera configurada entre publicaciones

# Ejecución del publicador
if __name__ == "__main__":
    try:
        # Puedes modificar los valores de espera, QoS y retain al llamar a la función
        publicar_datos(espera=5, qos=1, retain=False)  # Cambia los parámetros según tus necesidades
    except KeyboardInterrupt:
        print("Simulación terminada.")
        client.disconnect()
