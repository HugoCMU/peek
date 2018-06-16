import tensorflow as tf
import tensorflow.contrib.eager as tfe


class StarterModel(tf.keras.Model):
    """
    This model takes an image from the RPiZero camera and outputs servo commands
    """

    def __init__(self, input_shape, ckpt_path):
        super(StarterModel, self).__init__()
        # Train parameters
        self.ckpt_path = ckpt_path
        self.global_step = tf.train.get_or_create_global_step()
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
        self.head_2 = tf.keras.layers.Dense(1, kernel_initializer='normal')

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
        tf.contrib.eager.Saver(self.variables).save(self.ckpt_path + '/',
                                                    global_step=tf.train.get_or_create_global_step())

    def restore_tfe(self):
        print('Restoring model at %s' % self.ckpt_path)
        tf.contrib.eager.Saver(self.variables).restore(tf.train.latest_checkpoint(self.ckpt_path))

    def train(self, dataset, optimizer, load_ckpt=True, device='/gpu:0', log_steps=5, save_steps=50):
        if load_ckpt and tf.train.latest_checkpoint(self.ckpt_path):  # Will return None if no checkpoint found
            self.restore_tfe()
        with tf.device(device):
            for (i, (image, target)) in enumerate(tfe.Iterator(dataset)):
                tf.assign_add(self.global_step, 1)
                with tf.contrib.summary.record_summaries_every_n_global_steps(log_steps):
                    grads, loss = self.grad(image, target)
                    optimizer.apply_gradients(zip(grads, self.variables), global_step=self.global_step)
                    if i % log_steps == 0:
                        print(f'Step {self.global_step} Loss is {loss}')
                    if i % save_steps == 0:
                        self.save_tfe()
        self.save_tfe()
