"""
upload.py -- Sube un sketch a una placa MicroPython via OTA/MQTT.

Uso:
    python upload.py <archivo.py> as <dest.py> --board <nombre>

Ejemplo:
    python upload.py example.py as main.py --board example

Que hace:
    1. Calcula el md5 del archivo
    2. Levanta un HTTP server temporal sirviendo el archivo
    3. Publica en boards/<board> el JSON {url, dest, hash}
    4. Espera hasta que la placa descargue el archivo (o timeout)
    5. Cierra el HTTP server
"""

import argparse
import hashlib
import http.server
import json
import os
import socket
import sys
import threading
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env")) if os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", ".env")
) else None

MQTT_HOST = os.getenv("MQTT_HOST", "192.168.1.135")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((MQTT_HOST, 80))
        return s.getsockname()[0]
    finally:
        s.close()


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def serve_file(filepath, port, stop_event):
    """Sirve un unico archivo en GET / hasta que stop_event se active."""
    filename = os.path.basename(filepath)

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            print(f"[HTTP] Archivo servido a {self.client_address[0]}")
            stop_event.set()  # Detener tras primera descarga exitosa

        def log_message(self, format, *args):
            pass  # silenciar logs por defecto

    server = http.server.HTTPServer(("", port), Handler)
    server.timeout = 1
    while not stop_event.is_set():
        server.handle_request()
    server.server_close()
    print("[HTTP] Servidor cerrado.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Archivo .py a subir")
    parser.add_argument("as_kw", metavar="as", help="Literal 'as'")
    parser.add_argument("dest", help="Nombre destino en la placa (ej: main.py)")
    parser.add_argument("--board", required=True, help="Nombre de la placa")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout en segundos (default 60)")
    args = parser.parse_args()

    filepath = args.file
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.path.dirname(__file__), "..", filepath)
    filepath = os.path.normpath(filepath)

    if not os.path.exists(filepath):
        print(f"Error: no existe {filepath}")
        sys.exit(1)

    file_hash = md5_file(filepath)
    local_ip  = get_local_ip()
    topic     = f"boards/{args.board}"
    url       = f"http://{local_ip}:{HTTP_PORT}/{os.path.basename(filepath)}"

    print(f"[upload] Archivo : {filepath}")
    print(f"[upload] Destino : {args.dest}")
    print(f"[upload] Board   : {args.board}")
    print(f"[upload] Topico  : {topic}")
    print(f"[upload] URL     : {url}")
    print(f"[upload] MD5     : {file_hash}")

    # Evento: placa descargo el archivo
    downloaded = threading.Event()
    # Evento: placa confirmo OTA via MQTT
    confirmed  = threading.Event()

    # HTTP server en hilo separado
    http_thread = threading.Thread(target=serve_file, args=(filepath, HTTP_PORT, downloaded), daemon=True)
    http_thread.start()
    time.sleep(0.3)  # Dar tiempo al server a arrancar

    # MQTT
    result_holder = {}

    def on_message(client, userdata, msg):
        payload = msg.payload.decode()
        print(f"[MQTT] {msg.topic} -> {payload}")
        result_holder["result"] = payload
        confirmed.set()

    mc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mc.on_message = on_message
    mc.connect(MQTT_HOST, MQTT_PORT)
    mc.subscribe(topic)
    mc.loop_start()

    # Publicar OTA command
    payload = json.dumps({"url": url, "dest": args.dest, "hash": file_hash})
    mc.publish(topic, payload)
    print(f"[upload] OTA publicado. Esperando descarga (timeout {args.timeout}s)...")

    # Esperar confirmacion MQTT (placa publica 'true' o 'false')
    ok = confirmed.wait(timeout=args.timeout)
    mc.loop_stop()
    mc.disconnect()

    # Asegurar que HTTP cierre
    downloaded.set()
    http_thread.join(timeout=3)

    if ok:
        res = result_holder.get("result", "")
        if res == "true":
            print("[upload] OTA completado con exito.")
        else:
            print(f"[upload] La placa reporto error: {res}")
            sys.exit(1)
    else:
        print("[upload] Timeout: la placa no confirmo la descarga.")
        sys.exit(1)


if __name__ == "__main__":
    main()