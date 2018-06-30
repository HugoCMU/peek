#!/usr/bin/env python3
from time import sleep
import RPi.GPIO as GPIO

# Servo Configs
PAN = {'name': 'TOWER_PRO_MG995',
       'pin': 13,
       'min': 30,
       'max': 70,
       'sleep': 0.1,
       "frequency": 50}  # Hz

TILT = {'name': 'FUTABA_SG3003',
        'pin': 12,
        'min': 30,
        'max': 70,
        'sleep': 0.1,
        "frequency": 50}  # Hz


class Servo:

    def __init__(self, config):
        self.name = config['name']
        self.pin = config['pin']
        self.min = config['min']
        self.max = config['max']
        self.sleep = config['sleep']
        self.frequency = config['frequency']

        self.servo = GPIO.setup(self.pin, GPIO.OUT)

    def go_to(self, input):
        input = max(self.min, min(self.max, input))
        pwm = GPIO.PWM(self.servo, self.frequency)
        pwm.start(input)
        sleep(self.sleep)
        pwm.stop()

    def scan(self):
        print('Scanning servo %s' % self.name)
        for dc in range(0, 100, 5):
            self.go_to(dc)


class PanTilt:

    def __init__(self, pan_config, tilt_config):
        GPIO.setmode(GPIO.BCM)
        self.pan = Servo(pan_config)
        self.tilt = Servo(tilt_config)

    def update(self, input):
        assert all(isinstance(_, float) for _ in input), 'Input must be floats'
        assert all(0 <= _ <= 1 for _ in input), 'Input must be in (0, 1) range'
        assert len(input) == 2, 'There are only 2 servos to control'
        for i, servo in enumerate([self.pan, self.tilt]):
            servo.go_to(input[i])

    def test(self):
        print('Testing PAN servo')
        self.pan.scan()
        print('Testing TILT servo')
        self.tilt.scan()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        GPIO.cleanup()


if __name__ == '__main__':

    with PanTilt(PAN, TILT) as pantilt:
        pantilt.test()
