import asyncio
from bleak import BleakClient

# Konfiguration
ADDRESS = "8C:4B:14:84:DB:72"
UUID_WRITE = "0000ff05-0000-1000-8000-00805f9b34fb"

# Mapping der sprechenden Namen auf die IDs
COMMAND_IDS = {
    "start_weekday": 0x53,
    "start_weekend": 0x73,
    "duration_weekday": 0x44,
    "duration_weekend": 0x64,
    "mode": 0x4f,
    "light_warm": 0x31,
    "light_neutral": 0x32,
    "light_cool": 0x33
}

def create_packet(msg_id, value):
    """Erstellt das Datenpaket mit der 0x123-Checksumme."""
    val_h = (value >> 8) & 0xFF
    val_l = value & 0xFF
    checksum = (291 - (msg_id + val_h + val_l)) % 256
    return bytes([0xee, msg_id, val_h, val_l, checksum, 0xef])

async def set_greenbox_setting(client, setting_name, value):
    """Sendet einen spezifischen Einstellungs-Befehl an die Box."""
    if setting_name not in COMMAND_IDS:
        print(f"Fehler: Unbekannte Einstellung {setting_name}")
        return

    msg_id = COMMAND_IDS[setting_name]
    packet = create_packet(msg_id, value)
    
    print(f"Sende {setting_name}: {value} (Hex: {packet.hex()})")
    await client.write_gatt_char(UUID_WRITE, packet)
    await asyncio.sleep(0.3) # Kurze Pause zur Verarbeitung

async def main():
    try:
        async with BleakClient(ADDRESS) as client:
            print("Verbunden!")

            # --- BEISPIELE ZUR NUTZUNG ---

            # 1. Timer für Wochentage auf 08:00 Uhr setzen (UTC 700)
            # await set_greenbox_setting(client, "start_weekday", 800)

            # 2. Timer für Wochenende auf 09:30 Uhr setzen (UTC 830)
            # await set_greenbox_setting(client, "start_weekend", 830)

            # 3. Wochenende-Timer DEAKTIVIEREN
            # await set_greenbox_setting(client, "start_weekend", 0)

            # 4. Dauer für Wochentage auf 14 Stunden setzen
            # await set_greenbox_setting(client, "duration_weekday", 14)

            # 5. Dauer für Wochenende auf 12 Stunden setzen
            # await set_greenbox_setting(client, "duration_weekend", 12)

            print("Alle Befehle erfolgreich gesendet.")

    except Exception as e:
        print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    asyncio.run(main())