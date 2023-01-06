from machine import Pin
from neopixel import NeoPixel

NP = NeoPixel(Pin(14), 2)


def set_eye_color(tup):
    """Set eye's color."""
    print(tup)
    NP.fill(tup)
    NP.write()
