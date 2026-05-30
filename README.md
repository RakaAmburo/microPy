# microPy

Colección de sketches MicroPython para microcontroladores (ESP32, ESP8266, etc.).

## Filosofía

Cada sketch tiene un nombre descriptivo que indica su función.  
Al subir al board, se despliega como .

## Estructura

```
microPy/
├── boot.py          # Conexión WiFi al arranque (usa secrets.py)
├── otatools.py      # Actualización OTA vía HTTP
├── secrets.py       # Credenciales WiFi (NO incluido en git)
└── <sketch>.py      # Sketches específicos por función
```

## Uso

1. Copiar `secrets.py` al board con tus credenciales WiFi
2. Copiar `boot.py` al board (gestiona la conexión automática al arranque)
3. Copiar el sketch deseado como `main.py` al board
4. (Opcional) Usar `otatools.py` para actualizar `main.py` vía OTA sin cable

## OTA (Over The Air)

`otatools.py` permite actualizar `main.py` desde un servidor HTTP local:

```python
from otatools import ota_update
ota_update()  # descarga main.py desde el servidor y reinicia
```

Por defecto apunta a `http://192.168.1.157:8000/main.py`.  
Servir con: `python -m http.server 8000` en el directorio del proyecto.

## secrets.py

No incluido en git. Crear manualmente en el board:

```python
WIFI_SSID = "tu_red"
WIFI_PASS = "tu_password"
```