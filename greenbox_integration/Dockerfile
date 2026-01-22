# Builder-Stage für uv
FROM astral-sh/uv:latest AS uv_bin

# Basis-Image
FROM python:3.13-slim-bookworm

# Labels für Home Assistant
LABEL \
  io.hass.name="Greenbox MQTT Bridge" \
  io.hass.description="Bluetooth-zu-MQTT Bridge für BerlinGreen Greenbox" \
  io.hass.arch="aarch64|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.0.0"

# Kopiere uv
COPY --from=uv_bin /uv /uvx /bin/

# System-Abhängigkeiten für Bluetooth
# Wir benötigen dbus, um mit dem Bluetooth-Stack des Hosts zu sprechen
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    dbus \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installiere Abhängigkeiten
# Da wir im Container sind, nutzen wir --system
RUN uv pip install --system bleak paho-mqtt

# Script kopieren
COPY greenbox_bridge.py .

# Startbefehl
CMD [ "python3", "greenbox_bridge.py" ]