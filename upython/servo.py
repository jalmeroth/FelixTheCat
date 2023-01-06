from time import sleep
from machine import Pin, PWM


def wave():
    speed = 0.3
    front = 115
    middle = 77
    back = 40

    full = 4 * speed
    half = 3 * speed

    servo = PWM(Pin(4), freq=50, duty=middle)
    print(servo)
    sleep(full)
    # => middle
    servo.duty(back)
    sleep(half)
    # => back
    servo.duty(front)
    sleep(full)
    # => front
    servo.duty(back)
    sleep(full)
    # => back
    servo.duty(front)
    sleep(full)
    # => front
    servo.duty(middle)
    sleep(half)
    servo.deinit()
    sleep(1)
