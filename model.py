import tensorflow as tf
from aiy.vision.inference import ModelDescriptor
from aiy.vision.models import utils

_COMPUTE_GRAPH_NAME = 'face_detection.binaryproto'

def _reshape(array, width):
    assert len(array) % width == 0
    height = len(array) // width
    return [array[i * width:(i + 1) * width] for i in range(height)]


class Face(object):
    """Face detection result."""

    def __init__(self, bounding_box, face_score, joy_score):
        """Creates a new Face instance.

        Args:
          bounding_box: (x, y, width, height).
          face_score: float, face confidence score.
          joy_score: float, face joy score.
        """
        self.bounding_box = bounding_box
        self.face_score = face_score
        self.joy_score = joy_score

    def __str__(self):
        return 'face_score=%f, joy_score=%f, bbox=%s' % (self.face_score,
                                                         self.joy_score,
                                                         str(self.bounding_box))


def model():
    # Face detection model has special implementation in VisionBonnet firmware.
    # input_shape, input_normalizer, and compute_graph params have on effect.
    return ModelDescriptor(
        name='FaceDetection',
        input_shape=(1, 0, 0, 3),
        input_normalizer=(0, 0),
        compute_graph=utils.load_compute_graph(_COMPUTE_GRAPH_NAME))


def get_faces(result):
    """Returns list of Face objects decoded from the inference result."""
    assert len(result.tensors) == 3
    # TODO(dkovalev): check tensor shapes
    bboxes = _reshape(result.tensors['bounding_boxes'].data, 4)
    face_scores = result.tensors['face_scores'].data
    joy_scores = result.tensors['joy_scores'].data
    assert len(bboxes) == len(joy_scores)
    assert len(bboxes) == len(face_scores)
    return [
        Face(tuple(bbox), face_score, joy_score)
        for bbox, face_score, joy_score in zip(bboxes, face_scores, joy_scores)
    ]


class StarterModel(tf.keras.Model):
    """
    This model takes an image from the RPiZero camera and outputs servo commands
    """

    def __init__(self, input_shape):
        super(StarterModel, self).__init__()
        self.cnn_base = tf.keras.applications.mobilenet.MobileNet(input_shape=input_shape,
                                                                 # depth_multiplier=0.5,
                                                                 include_top=False,
                                                                 weights='imagenet',
                                                                 pooling='avg',
                                                                 )
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.head_1 = tf.keras.layers.Dense(128, kernel_initializer='normal', activation='relu')
        self.head_2 = tf.keras.layers.Dense(3, kernel_initializer='normal')

    def predict(self, x):
        x = self.cnn_base(x)
        x = self.bn1(x)
        x = self.head_1(x)
        x = self.bn2(x)
        x = self.head_2(x)
        return x

    def loss(self, x, target):
        output = self.predict(x)
        error = output - target
        return tf.reduce_mean(tf.square(error))

    def grad(self, x, target):
        with tf.contrib.eager.GradientTape() as tape:
            loss_value = self.loss(x, target)
            tf.contrib.summary.scalar('loss', loss_value)
        return tape.gradient(loss_value, self.variables), loss_value
