import tensorflow as tf


class PlantAgeModel(tf.keras.Model):
    """
    This model takes an image of the plant as input and regresses an age [0, 1)
    """

    def __init__(self):
        super(PlantAgeModel, self).__init__()
        self.encoder = tf.keras.applications.mobilenet.MobileNet(input_shape=(160, 160, 3),
                                                                 # depth_multiplier=0.5,
                                                                 include_top=False,
                                                                 weights='imagenet',
                                                                 pooling='avg',
                                                                 )
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.head_1 = tf.keras.layers.Dense(128, kernel_initializer='normal', activation='relu')
        self.head_2 = tf.keras.layers.Dense(1, kernel_initializer='normal')

    def predict(self, input):
        result = self.encoder(input)
        result = self.bn1(result)
        result = self.head_1(result)
        result = self.bn2(result)
        result = self.head_2(result)
        return result

    def loss(self, input, target):
        output = self.predict(input)
        error = output - target
        return tf.reduce_mean(tf.square(error))

    def grad(self, input, target):
        with tf.contrib.eager.GradientTape() as tape:
            loss_value = self.loss(input, target)
            tf.contrib.summary.scalar('loss', loss_value)
        return tape.gradient(loss_value, self.variables), loss_value
