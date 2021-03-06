from pathlib import Path
import re
import tensorflow as tf
# Repo specific imports
from model import StarterModel

# Dataset/Model specific parameters
DATASET = 'dataset_18-06-15-22'

# Training parameters
# MODEL_CKPT = 'model.ckpt'
IMAGE_SIZE = [160, 160, 3]
SHUFFLE_BUFFER = 4
NUM_EPOCHS = 10
LEARNING_RATE = 0.0001
BATCH_SIZE = 4

# Directories
root_dir = Path.cwd()
data_dir = root_dir / 'data' / DATASET
model_dir = root_dir / 'model'
log_dir = root_dir / 'log'


def _target_from_filename(filename):
    """
    Gets the target from image filename using regex. Dataset specific.
    :param filename: (str) image filename
    :return: (int) label in [0, 1]
    """
    # Sample filename: PSI_Tray031_2015-12-26--17-38-25_top.png
    filename_regex = re.search(r'\d+_([a-z]+).png', str(filename))
    str_label = filename_regex.groups()[0]
    label_dict = {'high': 1.0, 'low': 0.0}
    return label_dict[str_label]


def _parse_single(filename, label, image_size=IMAGE_SIZE):
    """
    Parse single data point (image, label)
    :param filename: (str) image filename
    :return: image, label
    """
    # Decode and convert image to appropriate type
    image = tf.image.decode_png(tf.read_file(filename), channels=image_size[2])
    image = tf.image.convert_image_dtype(image, tf.float32)  # Also scales from [0, 255] to [0, 1)
    # Resize according to module requirements
    image = tf.image.resize_images(image, image_size[:2])
    return image, label


def load_dataset(train_dir, shuffle_buffer=SHUFFLE_BUFFER, num_epochs=NUM_EPOCHS, batch_size=BATCH_SIZE):
    """
    Creates dataset object from a directory containing images
    :param train_dir: (Path) training data location
    :param shuffle_buffer: (int)
    :param num_epochs: (int)
    :param batch_size: (int)
    :return:
    """
    # Dataset creation from images (target is in filename)
    filenames = tf.constant(list(str(file) for file in train_dir.glob('*.png')))
    labels = list(map(_target_from_filename, train_dir.glob('*.png')))
    labels = tf.constant(labels)
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(lambda filename, label: _parse_single(filename, label))
    dataset = dataset.shuffle(shuffle_buffer).repeat(num_epochs).batch(batch_size)
    # dataset = dataset.apply(tf.contrib.data.prefetch_to_device('/gpu:0'))
    return dataset

if __name__ == '__main__':

    # Enable eager execution
    tfe = tf.contrib.eager
    tf.enable_eager_execution(device_policy=tfe.DEVICE_PLACEMENT_SILENT)

    # Model and optimizer
    model = StarterModel(input_shape=IMAGE_SIZE, ckpt_path=str(model_dir))
    optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)

    # Tensorboard summary writer
    writer = tf.contrib.summary.create_file_writer(str(log_dir))
    writer.set_as_default()

    # Load dataset
    dataset = load_dataset(data_dir)

    # Train the model
    model.train(dataset, optimizer)