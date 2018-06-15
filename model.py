import tensorflow as tf


class StarterModel(tf.keras.Model):
    """
    This model takes an image from the RPiZero camera and outputs servo commands
    """

    def __init__(self, input_shape, ckpt_path):
        super(StarterModel, self).__init__()

        self.ckpt_path = ckpt_path

        # Build the model layer by layer
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

    def save_tfe(self):
        print('Saving model at %s' % self.ckpt_path)
        tf.contrib.eager.Saver(self.variables).save(self.ckpt_path,
                                                    global_step=tf.train.get_or_create_global_step())

    def restore_tfe(self):
        print('Restoring model at %s' % self.ckpt_path)
        tf.contrib.eager.Saver(self.variables).restore(tf.train.latest_checkpoint(self.ckpt_path))

    def fit(self):
        pass
