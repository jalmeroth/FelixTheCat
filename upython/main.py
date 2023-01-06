"""Provice main routines."""
from math import sin
from machine import unique_id, Timer, reset
from ubinascii import hexlify

from umqtt_simple import MQTTClient, MQTTException

from net import do_connect
from led import set_eye_color
from config import Config
from servo import wave

CONFIG = Config()
COUNTER = 0
CAT_NAME = getattr(CONFIG, "CAT_NAME", "FelixTheCat")

MQTT_CLIENT_ID = hexlify(unique_id())
MQTT_KEEPALIVE = getattr(CONFIG, "MQTT_KEEPALIVE", 120)
MQTT_SERVER = getattr(CONFIG, "MQTT_SERVER", "test.mosquitto.org")
MQTT_CLIENT = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, keepalive=MQTT_KEEPALIVE)

MQTT_TOPIC_BASE = f"{CAT_NAME}"
MQTT_TOPIC_STATUS = f"{MQTT_TOPIC_BASE}/connected"

tim = Timer(-1)
tim.init(
    period=MQTT_KEEPALIVE * 1000,
    mode=Timer.PERIODIC,
    callback=lambda t: MQTT_CLIENT.ping(),
)


# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    """MQTT Callback."""
    print((topic, msg))
    wink()


def wink():
    """Wink."""
    global COUNTER

    r = int((1 + sin(COUNTER * 0.1324)) * 127)
    g = int((1 + sin(COUNTER * 0.1654)) * 127)
    b = int((1 + sin(COUNTER * 0.1)) * 127)

    tup = (r, g, b)
    COUNTER += 1

    set_eye_color(tup)
    wave()
    set_eye_color((0, 0, 0))


def main():
    """Provide main routine."""
    ssid = getattr(CONFIG, "WIFI_SSID")
    password = getattr(CONFIG, "WIFI_PASS")
    do_connect(ssid, password)
    MQTT_CLIENT.set_callback(sub_cb)
    MQTT_CLIENT.set_last_will(MQTT_TOPIC_STATUS, "0", True)
    MQTT_CLIENT.connect()
    MQTT_CLIENT.publish(MQTT_TOPIC_STATUS, "1", True)
    MQTT_CLIENT.subscribe(b"winkekatze/allcats/#")
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
