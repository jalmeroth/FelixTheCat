"""Provide Servo functions."""
from time import sleep
from machine import Pin, PWM
from const import SERVO_PIN


class Servo:
    """Represent a Servo."""

    back = 40
    front = 115
    middle = 77
    pause = 0.2

    def __init__(self) -> None:
        self.servo = PWM(Pin(SERVO_PIN), freq=50, duty=self.middle)

    def wave(self):
        """Wave arm."""
        sleep(self.pause)  # might move to middle
        self.servo.duty(self.front)
        sleep(self.pause)  # move to front
        self.servo.duty(self.back)
        sleep(3 * self.pause)  # move to back
        self.servo.duty(self.front)
        sleep(3 * self.pause)  # move to front
        self.servo.duty(self.back)
        sleep(3 * self.pause)  # move to back
        self.servo.duty(self.middle)
        sleep(self.pause)  # move to middle

    def __del__(self):
        self.servo.deinit()
