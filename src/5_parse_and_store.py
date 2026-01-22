import asyncio
import json
import time
from bleak import BleakClient

ADDRESS = "8C:4B:14:84:DB:72"
UUID_DATA = "0000ff05-0000-1000-8000-00805f9b34fb"

ID_MAP = {
    "31": "light_warm_white_percent",
    "32": "light_neutral_white_percent",
    "33": "light_cool_white_percent",
    "44": "timer_duration_hours_weekday",
    "4f": "operation_mode", # 0=ManAus, 1=ManAn, 3=TimerAn
    "53": "timer_start_utc_weekday",
    "54": "wifi_status_raw",
    "57": "water_level_percent",
    "64": "timer_duration_hours_weekend",
    "66": "unknown_66",
    "72": "unknown_72",
    "73": "timer_start_utc_weekend"
}
results = {}

def translate_mode(value):
    modes = {
        0: "Manuell AUS",
        1: "Manuell AN",
        3: "Timer AKTIV (Tag)",
        2: "Timer AKTIV (Nacht/Schlaf)" # Vermutung
    }
    return modes.get(value, f"Unbekannter Modus ({value})")

def handle_notifications(sender, data):
    if len(data) == 6 and data[0] == 0xee and data[5] == 0xef:
        msg_id_hex = f"{data[1]:02x}"
        value = (data[2] << 8) | data[3]
        
        # Checksumme validieren
        if (data[1] + data[2] + data[3] + data[4]) % 256 == (291 % 256):
            if msg_id_hex in ID_MAP:
                name = ID_MAP[msg_id_hex]
                
                # Spezial-Übersetzungen
                if name == "operation_mode":
                    results["operation_mode_text"] = translate_mode(value)
                    results[name] = value
                elif "timer_start_utc" in name:
                    results[name] = value
                    if value > 0:
                        h = (value // 100 + 1) % 24
                        results[f"{name.replace('utc', 'local')}"] = f"{h:02d}:{value % 100:02d}"
                    else:
                        results[f"{name.replace('utc', 'local')}"] = "Inaktiv"
                elif name == "water_level_raw":
                    results[name] = value
                    results["water_level_percent"] = round((value / 50) * 100, 1)
                else:
                    results[name] = value

async def main():
    print(f"Verbinde zu Greenbox...")
    async with BleakClient(ADDRESS) as client:
        await client.start_notify(UUID_DATA, handle_notifications)
        print("Sammle Daten (5s)... bitte ggf. Modus in der App kurz umschalten.")
        await asyncio.sleep(5)
        
        print("\n--- FINALES JSON FÜR HOME ASSISTANT ---")
        print(json.dumps(results, indent=4, sort_keys=True))

if __name__ == "__main__":
    asyncio.run(main())