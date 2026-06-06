import network, time
from umqtt.simple import MQTTClient
import ujson
from machine import Pin
import secrets
from otatools import ota_update, handle_ping, TOPIC_PING

# --- Configuracion --- python upload.py portero.py as main.py --board portero
MQTT_BROKER  = "192.168.1.135"
MQTT_PORT    = 1883
BOARD_NAME   = "portero"
TOPIC_OTA    = f"boards/{BOARD_NAME}"
TOPIC_CMD    = "casa/portero"
TOPIC_STATE  = "casa/portero/state"

relay = Pin(5, Pin.OUT)
relay_state = False
relay.value(0)

def set_relay(state):
    global relay_state
    relay_state = state
    relay.value(1 if state else 0)
    msg = "on" if state else "off"
    client.publish(TOPIC_STATE, msg)
    print(f"Rele: {msg}")

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
    m = msg.decode().strip()
    print(f"MQTT [{t}]: {m}")

    if handle_ping(t, client, BOARD_NAME):
        return

    if t == TOPIC_OTA:
        try:
            data = ujson.loads(m)
            ota_update(data["url"], data["dest"], data["hash"], client, TOPIC_OTA)
        except Exception as e:
            print("Error OTA:", e)

    elif t == TOPIC_CMD:
        if m == "on":
            set_relay(True)
        elif m == "off":
            set_relay(False)
        else:
            print("Comando desconocido:", m)

conectar_wifi()

client = MQTTClient(BOARD_NAME, MQTT_BROKER, MQTT_PORT)
client.set_callback(callback)
client.connect()
client.subscribe(TOPIC_OTA.encode())
client.subscribe(TOPIC_CMD.encode())
client.subscribe(TOPIC_PING.encode())
print(f"Escuchando en {TOPIC_OTA}, {TOPIC_CMD} y {TOPIC_PING}")

# Publicar estado inicial
client.publish(TOPIC_STATE, "off")

while True:
    client.check_msg()
    time.sleep(0.1)