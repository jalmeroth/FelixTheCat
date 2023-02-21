"""Provice main routines."""
import json
from machine import reset, unique_id
from ubinascii import hexlify

from umqtt.simple import MQTTException

from config import Config
from led import Eyes
from mqtt import Wrapper
from net import NetworkManager
from servo import Servo

CONFIG = Config()
SERVO_PIN = getattr(CONFIG, "SERVO_PIN", "5")
LED_PIN = getattr(CONFIG, "LED_PIN", "4")
LED_COUNT = getattr(CONFIG, "LED_COUNT", "2")
LED_ORDER = getattr(CONFIG, "LED_ORDER", None)  # RGB not GRB
EYES = Eyes(LED_PIN, LED_COUNT, LED_ORDER)
MQTT_CLIENT = Wrapper()
CAT_NAME = getattr(CONFIG, "CAT_NAME", "FelixTheCat")
MQTT_PREFIX = getattr(CONFIG, "MQTT_PREFIX", "winkekatze")

MQTT_CLIENT_ID = hexlify(unique_id())
MQTT_KEEPALIVE = getattr(CONFIG, "MQTT_KEEPALIVE", 120)
MQTT_SERVER = getattr(CONFIG, "MQTT_SERVER", "test.mosquitto.org")

MQTT_TOPIC_PREFIX = MQTT_PREFIX
MQTT_TOPIC_BASE = f"{MQTT_PREFIX}/{CAT_NAME}"
MQTT_TOPIC_CONNECTED = f"{MQTT_TOPIC_BASE}/connected"
MQTT_TOPIC_STATUS = f"{MQTT_TOPIC_BASE}/status"
MQTT_TOPIC_UPTIME = f"{MQTT_TOPIC_BASE}/uptime"
MQTT_TOPIC_ALLCATS = "winkekatze/allcats"


def update_config(data):
    """Update config."""
    config = {}
    try:
        config = json.loads(data)
    except TypeError:
        pass
    CONFIG.data.update(config)  # update running config
    CONFIG.save(CONFIG.data)  # persist running config


# Received messages from subscriptions will be delivered to this callback
def mqtt_message_handler(topic, msg):
    """MQTT Callback."""
    topic = topic.decode()
    msg = msg.decode()
    print((topic, msg))
    if (
        topic == MQTT_TOPIC_CONNECTED and msg == "1"
    ):  # we successfully subscribed ourselfs
        EYES.set_color("green")
        wink()
    elif topic == MQTT_TOPIC_ALLCATS or topic.endswith("command"):
        wink()
    elif topic.endswith("eye/set"):
        EYES.set_color(msg)
    elif topic == f"{MQTT_TOPIC_BASE}/config/set":
        update_config(msg)
    elif topic == f"{MQTT_TOPIC_BASE}/reset/set":
        reset()
    else:
        print("Meow.")


def wink():
    """Wink."""
    print("^-^/")
    MQTT_CLIENT.publish(MQTT_TOPIC_STATUS, "fishing")
    EYES.show()
    Servo(SERVO_PIN).wave()
    EYES.show("black")


def mqtt_connect_handler():
    """Handle MQTT connect event."""
    print("on_connect")
    MQTT_CLIENT.client.subscribe(f"{MQTT_TOPIC_ALLCATS}/#".encode())
    MQTT_CLIENT.client.subscribe(f"{MQTT_TOPIC_BASE}/#")
    MQTT_CLIENT.publish(MQTT_TOPIC_CONNECTED, "1", retain=True)


def main():
    """Provide main routine."""
    ssid = getattr(CONFIG, "WIFI_SSID", "")
    password = getattr(CONFIG, "WIFI_PASS", "")
    NetworkManager().do_connect(ssid, password, hostname=CAT_NAME)

    EYES.show("yellow")

    MQTT_CLIENT.DEBUG = True  # enable debug mode
    MQTT_CLIENT.on_connect = mqtt_connect_handler
    MQTT_CLIENT.on_message = mqtt_message_handler
    MQTT_CLIENT.set_last_will(MQTT_TOPIC_CONNECTED, "0", retain=True)

    while True:
        if not MQTT_CLIENT.connected:
            MQTT_CLIENT.connect(
                client_id=MQTT_CLIENT_ID, server=MQTT_SERVER, keepalive=MQTT_KEEPALIVE
            )
        MQTT_CLIENT.wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        MQTT_CLIENT.disconnect()
    except (OSError, MQTTException) as err:
        print(f"Resetting: {err}")
        with open("error.log", mode="a+", encoding="utf-8") as err_log:
            err_log.write(str(err))
        reset()
