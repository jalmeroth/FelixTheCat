"""Provide functions to control Eyes."""
from machine import Pin
from neopixel import NeoPixel

from const import COLORS


class Eyes:
    """Represent Eyes."""

    def __init__(self, led_pin, led_count, led_order=None) -> None:
        self.neo = NeoPixel(Pin(led_pin), led_count)
        if led_order is not None:
            self.neo.ORDER = tuple(led_order)
        self.show("white")

    def set_color(self, color):
        """Set eye's color."""
        if isinstance(color, str):
            color = COLORS.get(color)
        print(color)
        if color:
            self.neo.fill(color)

    def show(self, color=None):
        """Show Eye color."""
        if color:
            self.set_color(color)
        self.neo.write()
