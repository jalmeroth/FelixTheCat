"""Provide Servo functions."""
from time import sleep
from machine import Pin, PWM
from const import SERVO_PIN


class Servo:
    """Represent a Servo."""

    back = 50
    front = 100
    middle = 75
    pause = 0.2

    def wave(self):
        """Wave arm."""
        servo = PWM(Pin(SERVO_PIN), freq=50, duty=self.middle)
        sleep(self.pause)  # might move to middle
        servo.duty(self.front)
        sleep(self.pause)  # move to front
        servo.duty(self.back)
        sleep(3 * self.pause)  # move to back
        servo.duty(self.front)
        sleep(3 * self.pause)  # move to front
        servo.duty(self.back)
        sleep(3 * self.pause)  # move to back
        servo.duty(self.middle)
        sleep(3 * self.pause)  # move to middle
        servo.deinit()
