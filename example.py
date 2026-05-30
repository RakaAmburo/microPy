import network, time
from umqtt.simple import MQTTClient
import ujson
import secrets
from otatools import ota_update

# --- Configuracion ---
MQTT_BROKER = "192.168.1.135"
MQTT_PORT   = 1883
BOARD_NAME  = "example"
TOPIC_OTA   = f"boards/{BOARD_NAME}"

def conectar_wifi():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
    print("Conectando WiFi...", end="")
    while not sta.isconnected():
        time.sleep(0.5)
        print(".", end="")
    print("\nWiFi OK:", sta.ifconfig()[0])

def callback(topic, msg):
    print("MQTT:", topic, msg)
    try:
        data = ujson.loads(msg.decode())
        url  = data["url"]
        dest = data["dest"]
        hash = data["hash"]
        ota_update(url, dest, hash, client, TOPIC_OTA)
    except Exception as e:
        print("Error procesando OTA:", e)

conectar_wifi()

client = MQTTClient(BOARD_NAME, MQTT_BROKER, MQTT_PORT)
client.set_callback(callback)
client.connect()
client.subscribe(TOPIC_OTA.encode())
print(f"Escuchando OTA en {TOPIC_OTA}")

while True:
    client.check_msg()
    time.sleep(0.1)