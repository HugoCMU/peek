#!/usr/bin/env python3
"""Demonstrates simultaneous control of two servos on the hat.

One servo uses the simple default configuration, the other servo is tuned to
ensure the full range is reachable.
"""

from time import sleep
from gpiozero import Servo
from aiy.pins import PIN_A, PIN_B, PIN_C

# Each servo within the pan-tilt-rotate camera mount has its own object
pan_servo = Servo(PIN_A)
tilt_servo = Servo(PIN_B)
rot_servo = Servo(PIN_C)
servos = {'pan': pan_servo,
          'tilt': tilt_servo,
          'rot': rot_servo}

# Move the Servos back and forth until the user terminates the example.
while True:
    for name, servo in servos.items():
        print('Testing out servo %s' % name)
        servo.min()
        sleep(1)
        servo.mid()
        sleep(1)
        servo.max()
        sleep(1)
