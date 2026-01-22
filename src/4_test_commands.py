def parse_greenbox_data(data_hex):
    # Beispiel: ee5700329aef
    if len(data_hex) < 12: return None
    
    # Bytes extrahieren
    header = data_hex[0:2]
    msg_id = data_hex[2:4]
    value  = int(data_hex[4:8], 16)
    checksum = data_hex[8:10]
    footer = data_hex[10:12]
    
    if msg_id == "57":
        # Wasserstand: 50 = voll, 0 = leer
        percent = (value / 50) * 100
        return {"sensor": "water_level", "value": percent, "unit": "%"}
    
    elif msg_id == "31":
        # Licht-Intensität (64 hex = 100 dez)
        return {"sensor": "light_intensity", "value": value, "unit": "%"}
    
    elif msg_id == "53" or msg_id == "73":
        # Farbtemperatur (z.B. 0320 hex = 800)
        # Hier müssen wir noch die Umrechnung in Kelvin finden
        return {"sensor": "color_temp_raw", "value": value}

    return {"sensor": f"unknown_{msg_id}", "value": value}

# Test mit deinem Wert
raw = "ee5700329aef"
print(parse_greenbox_data(raw))
# Output: {'sensor': 'water_level', 'value': 100.0, 'unit': '%'}