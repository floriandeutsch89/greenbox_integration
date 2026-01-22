 # 🌱 Greenbox Berlin - Home Assistant Integration 
 
 Dieses Repository ermöglicht die vollständige Integration der BerlinGreen Greenbox in dein Home Assistant System via Bluetooth Low Energy (BLE) und MQTT. 
  
 ## Inhalt
 * greenbox_bridge/: Das eigentliche Home Assistant Add-on (Python 3.13 + MQTT). 
 * blueprints/: Gebrauchsfertige Automatisierungsvorlagen (z. B. für Wasserstands-Warnungen). 
 * repository.yaml: Die Konfigurationsdatei, damit Home Assistant dieses Repo als Add-on-Quelle erkennt. 
 
 ## Schnellstart 
 
 ### 1. Add-on installieren 
 1. Kopiere die URL dieses Repositories von GitHub. 
 2. Navigiere in Home Assistant zu Einstellungen -> Add-ons -> Add-on Store. 
 3. Klicke oben rechts auf das Menü (drei Punkte) -> Repositories. 
 4. Füge die URL hinzu, klicke auf Hinzufügen und installiere die Greenbox MQTT Bridge. 
 
 ### 2. Blueprints importieren 
 Du findest die Automatisierungsvorlagen im Ordner blueprints/. Kopiere den Link zur jeweiligen .yaml-Datei und importiere sie unter Einstellungen -> Automatisierungen -> Blueprints. 
 
 ## Struktur 
 
 ```text
 . 
 ├── repository.yaml # Meta-Daten für den Add-on Store 
 ├── greenbox_bridge/ # Source-Code & Docker-Config 
 └── blueprints/ # HA Automatisierungs-Vorlagen 
 ```
 
 ## Disclaimer 
 Dies ist ein inoffizielles Community-Projekt. Es besteht keine Verbindung zur BerlinGreen GmbH. Die Nutzung erfolgt auf eigene Gefahr.
