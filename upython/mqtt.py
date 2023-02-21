"""Provides a MQTT Client Wrapper."""
from machine import Timer
from umqtt.simple import MQTTClient, MQTTException


class Wrapper:
    """Wrap a MQTT client."""

    DEBUG = True

    def __init__(self) -> None:
        self.log("init")
        self.on_connect = self._on_connect
        self.on_message = self._on_message
        self.connected = False
        self.client = None
        self.timer = None
        self.lw_topic = None
        self.lw_message = None
        self.lw_qos = 0
        self.lw_retain = False

    def log(self, message):
        """Log a message."""
        if self.DEBUG:
            print(f"wrap:{message}")

    def _on_message(self, topic, message):
        """MQTT Message Handler"""
        self.log("_on_message")

    def _on_connect(self):
        """MQTT Connection Handler."""
        self.log("_on_connect")

    def connect(self, *args, **kwargs):
        """MQTT Connect."""
        self.log("connect")
        self.client = MQTTClient(*args, **kwargs)
        self.client.set_callback(self.on_message)
        if self.lw_topic is not None:
            self.client.set_last_will(
                topic=self.lw_topic,
                msg=self.lw_message,
                retain=self.lw_retain,
                qos=self.lw_qos,
            )
        try:
            self.client.connect()
        except (OSError, MQTTException) as err:
            self.log(f"Error: {err}")
        else:
            self.set_timer(kwargs.get("keepalive"))
            self.connected = True
            self.on_connect()

    def set_last_will(self, topic, message, retain=False, qos=0):
        """Define MQTT last will."""
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_message = message
        self.lw_qos = qos
        self.lw_retain = retain

    def set_timer(self, keepalive):
        """Setup a timer."""
        self.timer = Timer(0)
        self.timer.init(
            period=keepalive * 500,  # ping twice during KEEPALIVE
            mode=Timer.PERIODIC,
            callback=lambda t: self.ping(),
        )

    def ping(self):
        """Send uptime value."""
        self.log("ping")
        try:
            self.client.ping()
        except (OSError) as err:
            self.log(err)
            self.timer.deinit()

    def wait(self):
        """Wait for MQTT message."""
        self.log("wait")
        try:
            self.client.wait_msg()
        except (OSError, MQTTException) as err:
            print(f"Error: {err}")
            self.connected = False

    def disconnect(self):
        """MQTT Disconnect."""
        self.log("disconnect")
        self.client.disconnect()
        self.timer.deinit()
        self.connected = False

    def publish(self, *args, **kwargs):
        """Publish a message."""
        self.log("publish")
        if self.connected:
            self.log(f"<- {args[0]} {args[1]}")
            try:
                self.client.publish(*args, **kwargs)
            except (OSError, MQTTException) as err:
                print(f"Error: {err}")
                self.reconnect()
        else:
            self.log("not publishing")
