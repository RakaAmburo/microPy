"""
pub.py - Publicar un mensaje MQTT y esperar respuesta.
Uso: python pub.py <topic> <topic_respuesta> <mensaje>
"""
import sys, time, os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")) if os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", ".env")
) else None

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.135")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

if len(sys.argv) < 4:
    print("Uso: python pub.py <topic> <topic_respuesta> <mensaje>")
    sys.exit(1)

topic = sys.argv[1]
topic_resp = sys.argv[2]
message = " ".join(sys.argv[3:])

responses = []

def on_message(c, u, m):
    responses.append(m.payload.decode())
    print(f"[resp] {m.topic} -> {m.payload.decode()}")

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
c.on_message = on_message
c.connect(MQTT_HOST, MQTT_PORT)
c.subscribe(topic_resp)
c.loop_start()
time.sleep(0.3)
c.publish(topic, message)
print(f"[pub] {topic} -> {message}")
time.sleep(3)
c.loop_stop()
c.disconnect()

if not responses:
    print("[pub] Sin respuesta")