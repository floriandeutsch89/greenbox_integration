# Basis-Image: Aktuelles Python 3.13
FROM python:3.13-slim-bookworm

# Labels für Home Assistant
LABEL \
  io.hass.name="Greenbox MQTT Bridge" \
  io.hass.description="Bluetooth-zu-MQTT Bridge für BerlinGreen Greenbox" \
  io.hass.arch="aarch64|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.0.3"

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    dbus \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade uv

WORKDIR /app

# Abhängigkeiten mit uv installieren
# Wir kopieren die pyproject.toml nur, wenn sie existiert, 
# ansonsten installieren wir die Pakete direkt.
RUN uv pip install --system bleak paho-mqtt

# Script kopieren
COPY greenbox_bridge.py .

# Startbefehl
CMD [ "python3", "greenbox_bridge.py" ]