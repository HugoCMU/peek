import datetime
from picamera import PiCamera
from pathlib import Path

dataset_name = datetime.datetime.now().strftime('dataset_%y-%m-%d-%H')
dataset_path = Path.cwd() / 'data' / dataset_name
Path.mkdir(dataset_path)
print('Creating new dataset at %s' % str(dataset_path))

labels = ['high', 'low']
num_images_per_label = 10

with PiCamera() as cam:
    for label in labels:
        for i in range(num_images_per_label):
            image_name = datetime.datetime.now().strftime('%M%S_') + label + '.png'
            save_path = str(dataset_path / image_name)
            cam.capture(save_path, format='png')
            print(f'Image {i} of {num_images_per_label} for label {label} saved at {save_path}')
