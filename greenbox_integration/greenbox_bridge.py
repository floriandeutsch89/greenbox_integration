import asyncio
import json
import os
import logging
import paho.mqtt.client as mqtt
from bleak import BleakClient

# --- CONFIGURATION ---
def get_config():
    """Lädt Konfiguration aus HA-Optionen oder nutzt lokale Test-Werte."""
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        with open(options_path, "r") as f:
            return json.load(f)
    return {
        "ble_address": "8C:4B:14:84:DB:72",
        "mqtt_host": "localhost",  # IP des mqtt Brokers
        "mqtt_user": "",
        "mqtt_pass": "",
        "device_id": "greenbox_berlin",
        "device_name": "Greenbox Berlin",
        "debug": True  # beim debugging am PC standardmäßig an
    }

CONF = get_config()

# --- LOGGING SETUP ---
log_level = logging.DEBUG if CONF.get("debug") is True else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GreenboxBridge")

UUID_DATA = "0000ff05-0000-1000-8000-00805f9b34fb"

# Mapping der IDs auf Sensor-Namen
ID_MAP = {
    0x31: "light_warm", 
    0x32: "light_neutral", 
    0x33: "light_cool",
    0x44: "duration_weekday", 
    0x4f: "mode_id", 
    0x53: "start_weekday",
    0x54: "wifi_status",
    0x57: "water_percent", 
    0x64: "duration_weekend", 
    0x66: "unknown_66",
    0x72: "unknown_72",
    0x73: "start_weekend"
}

class GreenboxBridge:
    def __init__(self):
        self.ble_client = None
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.states = {}
        self.discovery_sent = False

    def calculate_checksum(self, msg_id, val_h, val_l):
        """Berechnet die Checksumme nach der 0x123 Regel."""
        # Summe ID + High + Low + CS = 291 (0x123)
        return (291 - (msg_id + val_h + val_l)) % 256

    def create_packet(self, msg_id, value):
        """Erstellt ein fertiges 6-Byte Paket für die Box."""
        val_h, val_l = (value >> 8) & 0xFF, value & 0xFF
        cs = self.calculate_checksum(msg_id, val_h, val_l)
        return bytes([0xee, msg_id, val_h, val_l, cs, 0xef])

    def send_discovery(self):
        """Registriert alle Sensoren automatisch in Home Assistant."""
        prefix = "homeassistant"
        dev_id = CONF['device_id']
        device = {
            "identifiers": [dev_id],
            "name": CONF['device_name'],
            "manufacturer": "BerlinGreen",
            "model": "Greenbox v1"
        }

        # Definition der Entities
        entities = [
            ("sensor", "water", "Wasserstand", "%", "{{ value_json.water_percent }}", "water"),
            ("sensor", "mode", "Betriebsmodus", None, "{{ value_json.mode_text }}", "enum"),
            ("sensor", "start_wd", "Timer Start (Mo-Fr)", None, "{{ value_json.start_weekday_local }}", "clock"),
            ("sensor", "start_we", "Timer Start (Sa-So)", None, "{{ value_json.start_weekend_local }}", "clock"),
        ]

        for platform, key, name, unit, tmpl, icon in entities:
            config = {
                "name": name,
                "unique_id": f"{dev_id}_{key}",
                "state_topic": f"{dev_id}/state",
                "value_template": tmpl,
                "device": device
            }
            if unit: config["unit_of_measurement"] = unit
            self.mqtt_client.publish(f"{prefix}/{platform}/{dev_id}/{key}/config", json.dumps(config), retain=True)

        # Spezial-Entity: Licht
        light_config = {
            "name": "Beleuchtung",
            "unique_id": f"{dev_id}_light",
            "command_topic": f"{dev_id}/light/set",
            "state_topic": f"{dev_id}/state",
            "schema": "template",
            "state_template": "{% if value_json.mode_id == 0 %}off{% else %}on{% endif %}",
            "command_on_template": "ON",
            "command_off_template": "OFF",
            "device": device
        }
        self.mqtt_client.publish(f"{prefix}/light/{dev_id}/light/config", json.dumps(light_config), retain=True)
        logger.info("HA Discovery Nachrichten gesendet.")

    async def handle_ble_notification(self, sender, data):

        logger.debug(f"BLE Raw Data: {data.hex()}")
        """Verarbeitet eingehende Bluetooth-Pakete."""
        if len(data) == 6 and data[0] == 0xee and data[5] == 0xef:
            msg_id, val_h, val_l, cs = data[1], data[2], data[3], data[4]
            
            # Checksum-Validierung
            if (msg_id + val_h + val_l + cs) % 256 == (291 % 256):
                val = (val_h << 8) | val_l
                key = ID_MAP.get(msg_id)

                if key:
                    logger.debug(f"Gültiges Paket: {key} = {val}")

                if not key: return

                self.states[key] = val
              
                if "start_" in key:
                    if val == 0:
                        self.states[f"{key}_local"] = "Inaktiv"
                    else:
                        # UTC -> Lokal (+1h für Winterzeit)
                        h = (val // 100 + 1) % 24
                        self.states[f"{key}_local"] = f"{h:02d}:{val % 100:02d}"
                
                if key == "mode_id":
                    modes = {0: "Manuell AUS", 1: "Manuell AN", 3: "Timer AKTIV"}
                    self.states["mode_text"] = modes.get(val, f"Status {val}")

                # Update an MQTT senden
                self.mqtt_client.publish(f"{CONF['device_id']}/state", json.dumps(self.states))

    def on_mqtt_message(self, client, userdata, msg):
        """Verarbeitet Steuerbefehle von Home Assistant."""
        payload = msg.payload.decode()
        logger.info(f"MQTT Befehl erhalten: {payload}")
        asyncio.run_coroutine_threadsafe(self.execute_light_command(payload), asyncio.get_event_loop())

    async def execute_light_command(self, payload):
        """Führt das Ein-/Ausschalten via BLE aus."""
        if not self.ble_client or not self.ble_client.is_connected:
            logger.warning("Befehl ignoriert: Keine Bluetooth-Verbindung.")
            return

        brightness = 100 if payload == "ON" else 0
        mode = 1 if payload == "ON" else 0

        # Alle 3 Kanäle setzen
        for channel_id in [0x31, 0x32, 0x33]:
            await self.ble_client.write_gatt_char(UUID_DATA, self.create_packet(channel_id, brightness))
            await asyncio.sleep(0.1)
        
        # Modus auf Manuell setzen
        await self.ble_client.write_gatt_char(UUID_DATA, self.create_packet(0x4f, mode))
        logger.info(f"Greenbox auf {payload} gesetzt.")

    async def mqtt_loop(self):
        """Verwaltet die MQTT-Verbindung."""
        if CONF['mqtt_user']:
            self.mqtt_client.username_pw_set(CONF['mqtt_user'], CONF['mqtt_pass'])
        
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(CONF['mqtt_host'], 1883)
        self.mqtt_client.subscribe(f"{CONF['device_id']}/light/set")
        self.send_discovery()

        while True:
            self.mqtt_client.loop(timeout=0.1)
            await asyncio.sleep(0.1)

    async def run(self):
        """Haupt-Loop: Hält MQTT und BLE am Laufen."""
        asyncio.create_task(self.mqtt_loop())
        
        while True:
            try:
                logger.info(f"Verbinde zu {CONF['ble_address']}...")
                async with BleakClient(CONF['ble_address'], timeout=20.0) as client:
                    self.ble_client = client
                    await client.start_notify(UUID_DATA, self.handle_ble_notification)
                    logger.info("BLE aktiv und verbunden. Warte auf NOTIFY-Daten...")
                    
                    while client.is_connected:
                        # Wir schicken alle 60s ein "Keep Alive" (Status-Abfrage ID 4f)
                        # Das triggert die Box, Daten zu senden, falls sie still ist
                        await client.write_gatt_char(UUID_DATA, bytes.fromhex("ee4f0000d4ef"))
                        await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Verbindungsfehler: {e}. Reconnect in 30s...")
                self.ble_client = None
                await asyncio.sleep(30)

if __name__ == "__main__":
    bridge = GreenboxBridge()
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        logger.info("Bridge beendet.")