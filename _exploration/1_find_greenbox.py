import asyncio
from bleak import BleakScanner

async def run():
    print("Starte Deep-Debug Scan (60 Sekunden)...")
    print("Achte auf Geräte mit hohem RSSI (z.B. -40 bis -60) oder Service UUID '00ff'.")
    print("-" * 90)

    found_addresses = {}

    def detection_callback(device, adv):
        addr = device.address
        if addr not in found_addresses:
            found_addresses[addr] = True
            
            # 1. Basis-Infos
            name = device.name or "KEIN NAME"
            rssi = adv.rssi
            
            # 2. Manufacturer Data (Oft steht hier die Hardware-ID versteckt)
            m_data = "Keine"
            if adv.manufacturer_data:
                m_data = {key: val.hex() for key, val in adv.manufacturer_data.items()}
            
            # 3. Service UUIDs (Wir suchen nach '00ff')
            services = adv.service_uuids if adv.service_uuids else []
            
            print(f"ADDR: {addr} | RSSI: {rssi:>4} dBm | NAME: {name}")
            if services:
                print(f"  -> Services: {services}")
            if m_data != "Keine":
                print(f"  -> Hersteller-Daten: {m_data}")
            
            # Spezieller Alarm für deine GreenBox Vermutung
            if "8c4b1484" in addr.lower().replace(":", "") or "00ff" in str(services).lower():
                print("  [!!!] MÖGLICHER TREFFER GEFUNDEN [!!!]")
            
            print("-" * 90)

    async with BleakScanner(detection_callback):
        await asyncio.sleep(60.0)

if __name__ == "__main__":
    asyncio.run(run())