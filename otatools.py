import machine, time, os, urequests, uhashlib, ubinascii

# --- OTA via MQTT ---
# Uso: ota_update(url, dest, expected_hash, mqtt_client, topic)
#   url           — URL HTTP donde bajar el archivo
#   dest          — nombre final en la placa (ej: 'main.py')
#   expected_hash — sha256 hex string para verificar integridad
#   mqtt_client   — instancia MQTTClient ya conectada (para publicar resultado)
#   topic         — topico donde publicar 'true'/'false'

def ota_update(url, dest, expected_hash, mqtt_client=None, topic=None):
    tmp_file = "_ota_tmp.py"
    def _publish(msg):
        if mqtt_client and topic:
            try:
                mqtt_client.publish(topic, msg)
            except Exception as e:
                print("MQTT publish error:", e)

    try:
        print("OTA: descargando", url)
        r = urequests.get(url)
        if r.status_code != 200:
            print("Error HTTP:", r.status_code)
            r.close()
            _publish("false")
            return False
        code = r.text
        r.close()

        if not code.strip():
            print("Error: archivo vacío")
            _publish("false")
            return False

        # Verificar hash sha256
        h = uhashlib.sha256(code.encode()).digest()
        actual_hash = ubinascii.hexlify(h).decode()
        if actual_hash != expected_hash:
            print("Hash no coincide:", actual_hash, "!=", expected_hash)
            _publish("false")
            return False

        # Escribir temporal
        with open(tmp_file, "w") as f:
            f.write(code)

        if os.stat(tmp_file)[6] == 0:
            print("Error: archivo temporal vacío")
            os.remove(tmp_file)
            _publish("false")
            return False

        # Reemplazar destino
        if dest in os.listdir():
            os.remove(dest)
        os.rename(tmp_file, dest)
        print("OTA OK:", dest, os.stat(dest)[6], "bytes")

        _publish("true")
        time.sleep(0.5)
        machine.reset()
        return True

    except Exception as e:
        print("Error OTA:", e)
        try:
            if tmp_file in os.listdir():
                os.remove(tmp_file)
        except:
            pass
        _publish("false")
        return False

# --- Ping generico ---
# Uso: handle_ping(topic, mqtt_client, board_name)
#   Llamar desde el callback MQTT cuando topic == "boards/ping"
#   Responde publicando board_name en "boards/pong"
TOPIC_PING = "boards/ping"
TOPIC_PONG = "boards/pong"

def handle_ping(topic, mqtt_client, board_name):
    if topic == TOPIC_PING:
        try:
            mqtt_client.publish(TOPIC_PONG, board_name)
            print("Ping respondido:", board_name)
        except Exception as e:
            print("Error ping:", e)
        return True
    return False