blueprint:
  name: "Greenbox Wasserstand Warnung"
  description: "Sendet eine Benachrichtigung, wenn der Wasserstand der Greenbox unter einen Schwellenwert fällt."
  domain: automation
  input:
    greenbox_sensor:
      name: Greenbox Wasserstand Sensor
      description: "Wähle den Wasserstand-Sensor deiner Greenbox aus."
      selector:
        entity:
          domain: sensor
          device_class: water # Falls im Script definiert, sonst weglassen
    threshold:
      name: Warnschwelle
      description: "Bei wie viel Prozent soll gewarnt werden?"
      default: 10
      selector:
        number:
          min: 1
          max: 50
          unit_of_measurement: "%"
    notify_device:
      name: Benachrichtigungs-Gerät
      description: "An welches Gerät soll die Warnung gesendet werden?"
      selector:
        device:
          filter:
            - integration: mobile_app

trigger:
  - platform: numeric_state
    entity_id: !input greenbox_sensor
    below: !input threshold

action:
  - domain: mobile_app
    type: notify
    device_id: !input notify_device
    title: "🌱 Greenbox braucht Wasser!"
    message: "Der Wasserstand deiner Greenbox ist auf {{ states(trigger.entity_id) }}% gefallen. Bitte nachfüllen."