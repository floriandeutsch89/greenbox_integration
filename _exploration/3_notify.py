import asyncio
import time
from bleak import BleakClient

ADDRESS = "8C:4B:14:84:DB:72"
CHARACTERISTIC_UUID = "0000ff05-0000-1000-8000-00805f9b34fb"

# Hier speichern wir die Ergebnisse: { "ID": "Letzter Wert (Helligkeit/Status)" }
captured_data = {}

def notification_handler(sender, data):
    # Ein gültiges Paket hat 6 Bytes: [EE, ID, VAL_H, VAL_L, CS, EF]
    if len(data) == 6 and data[0] == 0xee and data[5] == 0xef:
        msg_id = f"{data[1]:02x}"
        # Wir kombinieren die zwei Datenbytes zu einem Integer
        value = (data[2] << 8) | data[3]
        
        # Speichern im Dictionary (überschreibt alte Werte der gleichen ID)
        captured_data[msg_id] = value

async def collect_data(address):
    print(f"Verbinde zu {address}...")
    try:
        async with BleakClient(address) as client:
            print("Verbunden! Starte Datenaufnahme für 5 Sekunden...")
            
            # Notifications aktivieren
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            
            # 5 Sekunden warten
            start_time = time.time()
            while time.time() - start_time < 5:
                await asyncio.sleep(1)
                remaining = int(5 - (time.time() - start_time))
                if remaining % 5 == 0:
                    print(f"Noch {remaining} Sekunden...")

            await client.stop_notify(CHARACTERISTIC_UUID)
            
            print("\n" + "="*5)
            print("GEFUNDENE DATEN-PUNKTE:")
            print("="*5)
            # Dictionary sortiert nach ID ausgeben
            for msg_id in sorted(captured_data.keys()):
                val = captured_data[msg_id]
                print(f"ID {msg_id.upper()}: {val} (hex: {val:04x})")
            print("="*5)
            
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    asyncio.run(collect_data(ADDRESS))

# Licht aus:
# ID 31: 0 (hex: 0000)
# ID 32: 49 (hex: 0031)
# ID 33: 49 (hex: 0031)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)

# 100% Wachstum neutral / 4500K:
# ID 31: 100 (hex: 0064)
# ID 32: 100 (hex: 0064)
# ID 33: 100 (hex: 0064)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)

# 50% Medium neutral / 4500K:
# ID 31: 50 (hex: 0032)
# ID 32: 50 (hex: 0032)
# ID 33: 50 (hex: 0032)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)

# 33% Ambient warm / 3000K:
# ID 31: 99 (hex: 0063)
# ID 32: 0 (hex: 0000)
# ID 33: 0 (hex: 0000)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)

# 6000K (manuell):
# ID 31: 0 (hex: 0000)
# ID 32: 0 (hex: 0000)
# ID 33: 100 (hex: 0064)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)

# 5300K (manuell):
# ID 31: 0 (hex: 0000)
# ID 32: 49 (hex: 0031)
# ID 33: 49 (hex: 0031)
# ID 44: 13 (hex: 000d)
# ID 4F: 3 (hex: 0003)
# ID 53: 800 (hex: 0320)
# ID 54: 255 (hex: 00ff)
# ID 57: 50 (hex: 0032)
# ID 64: 12 (hex: 000c)
# ID 66: 2 (hex: 0002)
# ID 72: 1 (hex: 0001)
# ID 73: 800 (hex: 0320)