#!/usr/bin/env python3
import argparse

from aiy.vision.inference import CameraInference
from aiy.vision.inference import ModelDescriptor
from aiy.vision.models import utils
from picamera import PiCamera

_COMPUTE_GRAPH_NAME = 'face_detection.binaryproto'


def model_descriptor(graph_name):
    # Face detection model has special implementation in VisionBonnet firmware.
    # input_shape, input_normalizer, and compute_graph params have on effect.
    return ModelDescriptor(
        name='ModelDescriptor',
        input_shape=(1, 0, 0, 3),
        input_normalizer=(0, 0),
        compute_graph=utils.load_compute_graph(graph_name))


def get_action(result):
    """Returns list servo actions decoded from the inference result."""
    assert len(result.tensors) == 1
    # TODO(dkovalev): check tensor shapes
    # TODO: Previous actions, recurrent state, etc
    action = result.tensors['output'].data
    return action


def main():
    """Face detection camera inference example."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--num_frames',
        '-n',
        type=int,
        dest='num_frames',
        default=-1,
        help='Sets the number of frames to run for, otherwise runs forever.')
    args = parser.parse_args()

    with PiCamera() as camera:
        # Forced sensor mode, 1640x1232, full FoV. See:
        # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
        # This is the resolution inference run on.
        camera.sensor_mode = 4

        # Scaled and cropped resolution. If different from sensor mode implied
        # resolution, inference results must be adjusted accordingly. This is
        # true in particular when camera.start_recording is used to record an
        # encoded h264 video stream as the Pi encoder can't encode all native
        # sensor resolutions, or a standard one like 1080p may be desired.
        camera.resolution = (1640, 1232)

        # Start the camera stream.
        camera.framerate = 30
        camera.start_preview()

        with CameraInference(model_descriptor(_COMPUTE_GRAPH_NAME)) as inference:
            for i, result in enumerate(inference.run()):
                if i == args.num_frames:
                    break
                action = get_action(result)
                print('Iteration #%d: actions=%s' % (i, str(action)))


if __name__ == '__main__':
    main()
