import network, time
from umqtt.simple import MQTTClient
import ujson
import secrets
from otatools import ota_update

# --- Configuracion --- python upload.py example.py as main.py --board example
MQTT_BROKER  = "192.168.1.135"
MQTT_PORT    = 1883
BOARD_NAME   = "example"
TOPIC_OTA    = f"boards/{BOARD_NAME}"
TOPIC_CMD    = "comando"
TOPIC_RESP   = "respuesta"

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
    t = topic.decode()
    m = msg.decode()
    print(f"MQTT [{t}]: {m}")

    if t == TOPIC_OTA:
        try:
            data = ujson.loads(m)
            ota_update(data["url"], data["dest"], data["hash"], client, TOPIC_OTA)
        except Exception as e:
            print("Error OTA:", e)

    elif t == TOPIC_CMD:
        client.publish(TOPIC_RESP, f"ESP32 received pipi {m}")

conectar_wifi()

client = MQTTClient(BOARD_NAME, MQTT_BROKER, MQTT_PORT)
client.set_callback(callback)
client.connect()
client.subscribe(TOPIC_OTA.encode())
client.subscribe(TOPIC_CMD.encode())
print(f"Escuchando en {TOPIC_OTA} y {TOPIC_CMD}")

while True:
    client.check_msg()
    time.sleep(0.1)