import paho.mqtt.client as mqtt
import json
import random
import time

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion/"
topic_root2 = "/sensores"

# Configuración del cliente MQTT
client = mqtt.Client()
client.connect(broker_address, broker_port)

# Función para generar datos aleatorios
def generar_datos(maquina_id):
    datos = {
        "id": maquina_id,
        "temperatura": round(random.uniform(20.0, 40), 2),
        "presion": round(random.uniform(1000,1020), 2),
        "Velocidad": round(random.uniform(0, 70), 2),
        "Direccion": round(random.uniform(0,360),2) 
    }
    return datos

# Publicación de datos
def publicar_datos():
    num_maquinas = 5
    while True:
        for maquina_id in range(101, num_maquinas+100):
            datos = generar_datos(maquina_id)
            topic = topic_root+str(maquina_id)+topic_root2
            client.publish(topic, json.dumps(datos))
            print(f"Publicado en {topic}: {datos}")
        time.sleep(1)  # Espera 1 segundos antes de generar los próximos datos

# Ejecución del publicador
if __name__ == "__main__":
    try:
        publicar_datos()
    except KeyboardInterrupt:
        print("Simulación terminada.")
        client.disconnect()