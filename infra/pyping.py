"""
pyping.py -- Hace ping a todas las boards MicroPython conectadas via MQTT.

Uso:
    python pyping.py [--timeout 3]

Publica en boards/ping y captura todas las respuestas en boards/pong.
"""

import os
import sys
import time
import argparse
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")) if os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", ".env")
) else None

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.135")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PING = "boards/ping"
TOPIC_PONG = "boards/pong"

def main():
    parser = argparse.ArgumentParser(description="Ping a todas las boards MicroPython")
    parser.add_argument("--timeout", type=float, default=3.0, help="Segundos de espera para respuestas (default: 3)")
    args = parser.parse_args()

    responses = []

    def on_connect(client, userdata, flags, rc):
        client.subscribe(TOPIC_PONG)

    def on_message(client, userdata, msg):
        board = msg.payload.decode().strip()
        if board not in responses:
            responses.append(board)
            print(f"  -> {board}")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    # Esperar conexion
    time.sleep(0.5)

    print(f"[pyping] Enviando ping a todas las boards...")
    client.publish(TOPIC_PING, "")

    time.sleep(args.timeout)
    client.loop_stop()
    client.disconnect()

    print(f"[pyping] {len(responses)} board(s) respondieron: {responses if responses else 'ninguna'}")

if __name__ == "__main__":
    main()