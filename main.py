import requests
import paho.mqtt.client as mqtt
import config
import time
import json

DEVICE_ID = "hitron_cable_modem"
DISCOVERY_PREFIX = "homeassistant"

def login_session():
    session = requests.Session()
    try:
        # Trigger login POST
        r = session.post(
            f"{config.MODEM_URL}/goform/home",
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0"
            },
            data={
                "user": "nologin",
                "pws": "nologin"
            },
            timeout=5
        )
        session.cookies.set("userid", r.cookies.get("userid"))
        print(f"Login OK, session: {session.cookies.get_dict()}")
        return session
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def extract_json_data(session, endpoint):
    try:
        res = session.get(
            f"{config.MODEM_URL}/data/{endpoint}",
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=5
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def publish_discovery(topic, key, unit, mqtt_client, name=None, device_class=None, state_class="measurement"):
    entity_id = topic.replace("/", "_")
    sensor_name = name or key.replace("_", " ").title()
    payload = {
        "name": sensor_name,
        "state_topic": topic,
        "unique_id": f"{DEVICE_ID}_{entity_id}",
        "unit_of_measurement": unit,
        "device_class": device_class,
        "state_class": state_class,
        "device": {
            "identifiers": [DEVICE_ID],
            "name": "Hitron Cable Modem",
            "model": "CODA",
            "manufacturer": "Hitron"
        }
    }
    mqtt_client.publish(
        f"{DISCOVERY_PREFIX}/sensor/{DEVICE_ID}/{entity_id}/config",
        json.dumps(payload),
        retain=True
    )

def publish_to_mqtt(topic_prefix, data, mqtt_client):
    def publish_recursive(prefix, obj):
        if isinstance(obj, dict):
            for key, val in obj.items():
                publish_recursive(f"{prefix}/{key}", val)
        elif isinstance(obj, list):
            for i, val in enumerate(obj):
                if isinstance(val, dict):
                    for k, v in val.items():
                        subtopic = f"{prefix}_{i}/{k}".lower()
                        mqtt_client.publish(subtopic, str(v), retain=True)
                        # Home Assistant auto-discovery
                        if k.lower() in ("snr", "signalStrength", "repPower", "repPower1_6"):
                            publish_discovery(subtopic, k, "dB" if "snr" in k.lower() else "dBmV", mqtt_client)
                        elif k.lower() in ("correcteds", "uncorrect", "dsoctets"):
                            publish_discovery(subtopic, k, "count" if "octets" not in k else "B", mqtt_client, state_class="total_increasing")
                        elif k.lower() in ("frequency", "channelBw", "bandwidth"):
                            publish_discovery(subtopic, k, "Hz", mqtt_client)
                        elif k.lower() in ("modulation", "modtype", "state"):
                            publish_discovery(subtopic, k, None, mqtt_client, state_class="measurement")
                else:
                    mqtt_client.publish(f"{prefix}/{i}", str(val), retain=True)
        else:
            mqtt_client.publish(prefix, str(obj), retain=True)

    publish_recursive(topic_prefix, data)

if __name__ == "__main__":
    mqtt_client = mqtt.Client(client_id="", protocol=mqtt.MQTTv5)
    mqtt_client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
    mqtt_client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)

    session = login_session()
    if not session:
        exit(1)

    pages = {
        "modem/dsinfo": "dsinfo.asp",
        "modem/usinfo": "usinfo.asp",
        "modem/system_model": "system_model.asp",
        "modem/usofdminfo": "usofdminfo.asp",
        "modem/dsofdminfo": "dsofmodinfo.asp",
        "modem/statuslog": "status_log.asp",
        "modem/cminit": "getCMInit.asp",
        "modem/link_status": "getLinkStatus.asp",
    }

    for topic, endpoint in pages.items():
        data = extract_json_data(session, endpoint)
        print(f"Extracted data from {endpoint}: {data}")
        publish_to_mqtt(topic, data, mqtt_client)

    mqtt_client.disconnect()
