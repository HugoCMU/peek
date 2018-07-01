#!/usr/bin/env python3
from time import sleep
import RPi.GPIO as GPIO

# Servo Configs
PAN = {'name': 'TOWER_PRO_MG995',
       'pin': 12,
       'min': 8.0,
       'max': 13.0,
       'sleep': 1.0,
       "frequency": 50}  # Hz

TILT = {'name': 'FUTABA_SG3003',
        'pin': 13,
        'min': 5.0,
        'max': 10.0,
        'sleep': 1.0,
        "frequency": 50}  # Hz


class Servo:

    def __init__(self, config):
        self.name = config['name']
        self.pin = config['pin']
        self.min = config['min']
        self.max = config['max']
        self.sleep = config['sleep']
        self.frequency = config['frequency']

        GPIO.setup(self.pin, GPIO.OUT)

    def go_to(self, input):
        # Clip the input between [0, 1], convert into duty cycles
        input = max(0.0, min(1.0, input))
        input = self.min + input * (self.max - self.min)
        # TODO: Better way of doing this that doesn't involve sleep?
        pwm = GPIO.PWM(self.pin, self.frequency)
        print('Sending %s servo to %f' % (self.name, input))
        pwm.start(input)
        sleep(self.sleep)
        pwm.stop()

    def scan(self):
        print('Scanning servo %s' % self.name)
        for dc in range(0, 100, 1):
            float_input = dc / 100.0
            self.go_to(float_input)


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
