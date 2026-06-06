"""
pub.py - Publicar un mensaje MQTT rapido.
Uso: python pub.py <topic> <mensaje>
"""
import sys
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")) if os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", ".env")
) else None

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.135")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

if len(sys.argv) < 3:
    print("Uso: python pub.py <topic> <mensaje>")
    sys.exit(1)

topic = sys.argv[1]
message = " ".join(sys.argv[2:])

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
c.connect(MQTT_HOST, MQTT_PORT)
c.loop_start()
time.sleep(0.3)
c.publish(topic, message)
time.sleep(0.5)
c.loop_stop()
c.disconnect()
print(f"[pub] {topic} -> {message}")