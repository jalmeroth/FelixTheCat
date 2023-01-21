"""Provice main routines."""
from machine import unique_id, Timer, reset
from time import time
from ubinascii import hexlify
import json

from umqtt_simple import MQTTClient, MQTTException

from net import do_connect
from led import Eyes
from config import Config
from servo import Servo

EYES = Eyes()
CONFIG = Config()
CAT_NAME = getattr(CONFIG, "CAT_NAME", "FelixTheCat")
MQTT_PREFIX = getattr(CONFIG, "MQTT_PREFIX", "winkekatze")

MQTT_CLIENT_ID = hexlify(unique_id())
MQTT_KEEPALIVE = getattr(CONFIG, "MQTT_KEEPALIVE", 120)
MQTT_SERVER = getattr(CONFIG, "MQTT_SERVER", "test.mosquitto.org")
MQTT_CLIENT = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=MQTT_KEEPALIVE)

MQTT_TOPIC_PREFIX = MQTT_PREFIX
MQTT_TOPIC_BASE = f"{MQTT_PREFIX}/{CAT_NAME}"
MQTT_TOPIC_CONNECTED = f"{MQTT_TOPIC_BASE}/connected"
MQTT_TOPIC_STATUS = f"{MQTT_TOPIC_BASE}/status"
MQTT_TOPIC_UPTIME = f"{MQTT_TOPIC_BASE}/uptime"
MQTT_TOPIC_ALLCATS = "winkekatze/allcats"

tim = Timer(-1)
tim.init(
    period=MQTT_KEEPALIVE * 1000,
    mode=Timer.PERIODIC,
    callback=lambda t: send_uptime(),
)


def send_uptime():
    """Send uptime value."""
    MQTT_CLIENT.publish(MQTT_TOPIC_UPTIME, str(time()))  # roll over after X


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
def message_handler(topic, msg):
    """MQTT Callback."""
    topic = topic.decode()
    msg = msg.decode()
    print((topic, msg))
    if topic == MQTT_TOPIC_CONNECTED:  # we successfully subscribed ourselfs
        EYES.set_color("green")
        wink()
    elif topic == MQTT_TOPIC_ALLCATS or topic.endswith("command"):
        wink()
    elif topic.endswith("eye/set"):
        EYES.set_color(msg)
    elif topic == f"{MQTT_TOPIC_BASE}/config/set":
        update_config(msg)
    else:
        print("Meow.")


def wink():
    """Wink."""
    print("^-^/")
    MQTT_CLIENT.publish(MQTT_TOPIC_STATUS, "fishing")
    EYES.show()
    Servo().wave()
    EYES.show("black")


def main():
    """Provide main routine."""
    ssid = getattr(CONFIG, "WIFI_SSID", "")
    password = getattr(CONFIG, "WIFI_PASS", "")
    do_connect(ssid, password)
    EYES.show("yellow")
    MQTT_CLIENT.set_callback(message_handler)
    MQTT_CLIENT.set_last_will(MQTT_TOPIC_CONNECTED, "0", True)
    MQTT_CLIENT.connect()
    MQTT_CLIENT.publish(MQTT_TOPIC_CONNECTED, "1", True)
    MQTT_CLIENT.subscribe(f"{MQTT_TOPIC_ALLCATS}/#".encode())
    MQTT_CLIENT.subscribe(f"{MQTT_TOPIC_BASE}/#".encode())

    while True:
        # Non-blocking wait for message
        MQTT_CLIENT.wait_msg()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        MQTT_CLIENT.disconnect()
    except (OSError, MQTTException) as err:
        print(f"Resetting: {err}")
        reset()
