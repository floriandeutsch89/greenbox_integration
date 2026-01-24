FROM python:3.13-slim-bookworm

LABEL \
  io.hass.name="Greenbox MQTT Bridge" \
  io.hass.description="Bluetooth-to-MQTT Bridge for BerlinGreen Greenbox" \
  io.hass.arch="aarch64|amd64|armv7" \
  io.hass.type="addon" \
  io.hass.version="1.10.0"

# Install System dependencies + gosu
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluez \
    dbus \
    libglib2.0-0 \
    gosu \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade uv

WORKDIR /app

# Install dependencies
RUN uv pip install --system bleak paho-mqtt

# Create non-root user (using a specific UID is safer for permission mapping)
RUN useradd -u 1000 --create-home --shell /bin/sh ha_user

COPY greenbox_bridge.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# The entrypoint handles the permission fix and user switch
ENTRYPOINT ["/entrypoint.sh"]

# The CMD is passed as arguments to the entrypoint.sh
CMD [ "python3", "greenbox_bridge.py" ]