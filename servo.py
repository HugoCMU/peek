#!/usr/bin/env python3
from time import sleep
import argparse
import gpiozero
from aiy.vision.pins import PIN_A, PIN_B

# Servo Types
TOWER_PRO_SG90 = {'name': 'tower_pro', 'min_pulse_width': 0.00033, 'max_pulse_width': 0.00253, "frequency": 0.1}
FUTABA_SG3003 = {'name': 'futaba', 'min_pulse_width': 0.0005, 'max_pulse_width': 0.00230, "frequency": 0.02}


class Servo():
    max_velocity = 2  # Maximum angular velocity
    min_pulse_width = 0.5
    max_pulse_width = 2.3

    def __init__(self, name, pin, angles, servo_type):
        self.name = name
        self.angles = angles
        self.type = servo_type
        self.min = angles['min']
        self.max = angles['max']
        self.min_clip = angles['min_clip']
        self.max_clip = angles['max_clip']
        self.range = angles['max'] - angles['min']
        self.servo = gpiozero.AngularServo(pin,
                                           min_pulse_width=servo_type['min_pulse_width'],
                                           max_pulse_width=servo_type['max_pulse_width'],
                                           # frame_width=servo_type['frequency'],
                                           min_angle=angles['min'],
                                           max_angle=angles['max'])

    def go_to(self, input):
        current_angle = self.servo.angle
        un_normalized = self.min + input * self.range
        angle_delta = current_angle - un_normalized
        velocity_clipped = min(max(angle_delta, -self.max_velocity), self.max_velocity)
        self.servo.angle = current_angle + velocity_clipped


# Run calibration 'servo.py -c' to get new servo values
PAN = {'max': 20, 'min': -20, 'max_clip': 10, 'min_clip': -10}
TILT = {'max': 20, 'min': -20, 'max_clip': 10, 'min_clip': -10}
servos = [Servo('pan', PIN_A, PAN, TOWER_PRO_SG90),
          Servo('tilt', PIN_B, TILT, FUTABA_SG3003)]


def update(input):
    assert all(isinstance(_, float) for _ in input), 'Input must be floats'
    assert all(0 <= _ <= 1 for _ in input), 'Input must be in (0, 1) range'
    assert len(input) == 2, 'There are only 2 servos to control'
    for i, x in enumerate(input):
        servos[i].go_to(x)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--calibrate',
        '-c',
        action='store_true',
        dest='calibrate',
        default=False,
        help='Calibrate servos.')
    args = parser.parse_args()

    if args.calibrate:
        calibration_output = []
        for servo in servos:
            print('-----------Calibration for %s ----------' % servo.name)
            servo.servo.mid()
            sleep(2)

            print('MEASURE MINIMUM ANGLE')
            servo.servo.min()
            min_angle = int(input('Minimum angle?'))
            min_clip_angle = int(input('What would you like to clip it to?'))

            print('MEASURE MAXIMUM ANGLE')
            servo.servo.max()
            max_angle = int(input('Maximum angle?'))
            max_clip_angle = int(input('What would you like to clip it to?'))
            calibration_output += ["%s = {'max': %d, 'min': %d, 'max_clip': %d, 'min_clip': %d}"
                                   % (servo.name, max_angle, min_angle, max_clip_angle, min_clip_angle)]
            print('-----------Calibration Complete----------')

        print('Copy paste the following line into servo.py:')
        for s in calibration_output:
            print(s)

    else:
        # Move the Servos back and forth until the user terminates the example.
        while True:
            for servo in servos:
                print('Servo %s, type %s' % (servo.name, servo.type['name']))
                print('MIN')
                servo.servo.min()
                sleep(2)
                print('MAX')
                servo.servo.max()
                sleep(2)
                print('MID')
                servo.servo.mid()
                sleep(2)

            # for _ in range(100):
            #     update([1.0, 1.0])
            # for _ in range(100):
            #     update([1.0, 0.0])
            # for _ in range(100):
            #     update([0.0, 1.0])
            # for _ in range(100):
            #     update([0.0, 0.0])
