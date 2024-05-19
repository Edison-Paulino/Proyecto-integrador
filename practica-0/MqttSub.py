import paho.mqtt.client as mqtt
import json

# Configuración del broker MQTT
broker_address = "test.mosquitto.org"
broker_port = 1883
topic_root = "estacion/#"

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
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el mensaje: {e}")

# Configuración del cliente MQTT
client = mqtt.Client()
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