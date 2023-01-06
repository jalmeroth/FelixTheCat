"""Provide functions to control Eyes."""
from machine import Pin
from neopixel import NeoPixel

from const import COLORS, LED_COUNT, LED_PIN, LED_ORDER


class Eyes:
    """Represent Eyes."""

    def __init__(self) -> None:
        self.neo = NeoPixel(Pin(LED_PIN), LED_COUNT)
        self.neo.ORDER = LED_ORDER
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
