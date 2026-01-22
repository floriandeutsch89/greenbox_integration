 # Greenbox Berlin - Home Assistant MQTT Bridge 
 
 Diese Bridge ermöglicht die nahtlose Einbindung deiner BerlinGreen Greenbox in Home Assistant. Sie nutzt Bluetooth Low Energy (BLE) für die Kommunikation mit der Box und MQTT für die Integration in Home Assistant. 
  
 ## Features 
 
 * Python 3.13 und uv für schnelle Installation und Ausführung. 
 * Native HA-Integration: Dank MQTT Discovery werden Sensoren und Lichtschalter automatisch ohne manuelle YAML-Konfiguration erkannt. 
 * Echtzeit-Monitoring: Wasserstand (%), Betriebsmodus (Timer vs. Manuell), und Lichtstatus. 
 * Vollständige Kontrolle: Licht ein/aus (alle Kanäle), Helligkeitssteuerung und zukünftig Timer-Programmierung. 
 * Resilienz: Automatischer Reconnect bei Verbindungsverlust und robuste Checksummen-Validierung. 
 
 ## Voraussetzungen 
 * Hardware: PC oder Server mit Bluetooth-Adapter in Reichweite der Greenbox. 
 * Software: uv, Docker (für HA Add-on Betrieb). 
 * Infrastruktur: Ein laufender MQTT Broker (z.B. Mosquitto). 
 
 ## Installation (Lokal am PC) 
 
 1. Ordner initialisieren: 
 ```bash
 uv init . 
 uv add bleak paho-mqtt 
 ```
 2. Script konfigurieren: 
 Die get_config() Funktion in greenbox_bridge.py prüft automatisch auf eine /data/options.json (HA Add-on Modus). Falls nicht vorhanden, werden die lokalen Fallback-Werte genutzt. 
 3. Starten:
 ```bash 
 uv run greenbox_bridge.py 
 ```
 
 ## Installation als Home Assistant Add-on 

 1. Kopiere die URL dieses GitHub-Repositories. 
 2. Gehe in Home Assistant auf Einstellungen -> Add-ons -> Add-on Store. 
 3. Klicke oben rechts auf die drei Punkte (Menü) und wähle Repositories. 
 4. Füge deine GitHub-URL hinzu und klicke auf Hinzufügen. 
 5. Installiere die "Greenbox MQTT Bridge". 
 
##  Konfiguration 
 
 Im Reiter Konfiguration müssen die ble_address und die MQTT-Zugangsdaten deines HA-Users hinterlegt werden. 

In den Add-on Optionen kannst du folgende Einstellungen vornehmen: 
 
 * ble_address: MAC-Adresse deiner Box. 
 * mqtt_host: Host deines Brokers (Standard: core-mosquitto). 
 * debug: (Boolean) Aktiviert ausführliche Logs. 
 
 ## Fehlersuche (Debug-Mode) 
 
 Wenn keine Daten in Home Assistant ankommen, aktiviere den debug-Modus in der Add-on Konfiguration und starte das Add-on neu. 
 
 Im Reiter Protokoll siehst du dann jede einzelne Bluetooth-Nachricht (BLE Raw Data), die von der Box empfangen wird. Dies hilft festzustellen, ob die Verbindung physikalisch besteht, aber die Datenverarbeitung (z.B. Checksumme) fehlschlägt.
 
 ## Technische Spezifikationen (Reverse Engineering) 
 
 ### Protokoll-Logik 
 Die Kommunikation erfolgt über binäre 6-Byte-Pakete. 
 
 * Checksummen-Formel: (ID + Data_High + Data_Low + Checksum) % 256 == 35 (Entspricht der Summe 0x123). 
 * Uhrzeit: Die Box arbeitet intern mit UTC. Für die lokale Anzeige (CET) wird im Script ein Offset von +1 Stunde angewendet. 
 
 ### ID-Mapping 
 | ID (Hex) | Funktion | Wertebereich | 
 | :--- | :--- | :--- | 
 | 0x31-0x33 | Lichtkanäle (Warm, Neutral, Kalt) | 0 - 100 | 
 | 0x4f | Betriebsmodus | 0=ManAus, 1=ManAn, 3=Timer | 
 | 0x57 | Wasserstand (Rohwert) | 0 - 50 | 
 | 0x53 | Timer Start (Mo-Fr) | UTC (z.B. 700 = 08:00 CET) | 
 | 0x73 | Timer Start (Sa-So) | UTC oder 0 (Inaktiv) | 
 
 ## Lizenz & Disclaimer 
 Dieses Projekt ist unabhängig von BerlinGreen entwickelt. Nutzung auf eigene Gefahr.