import asyncio
from bleak import BleakClient

# Deine exakte Adresse
ADDRESS = "8C:4B:14:84:DB:72"

async def main(address):
    print(f"Versuche Verbindung zu {address} aufzubauen...")
    # Wir erhöhen den Timeout, weil das Signal so schwach ist
    async with BleakClient(address, timeout=20.0) as client:
        print(f"Verbunden: {client.is_connected}")
        
        services = client.services
        for service in services:
            if "00ff" in service.uuid.lower():
                print(f"\n[INTERESSANTER SERVICE] {service.uuid}")
                for char in service.characteristics:
                    # Wir versuchen, jede Characteristic einmal zu lesen
                    value = ""
                    if "read" in char.properties:
                        try:
                            raw_val = await client.read_gatt_char(char.uuid)
                            value = f"| Wert (Hex): {raw_val.hex()}"
                        except:
                            value = "| Nicht lesbar"
                    
                    print(f"  -> Char: {char.uuid} | Props: {','.join(char.properties)} {value}")

if __name__ == "__main__":
    asyncio.run(main(ADDRESS))