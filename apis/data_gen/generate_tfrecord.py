import os
import io
import pandas as pd
import tensorflow as tf
from PIL import Image

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util
from collections import namedtuple
import argparse


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path, category_idx):
    with tf.io.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(float(row['xmin']) / width)
        xmaxs.append(float(row['xmax']) / width)
        ymins.append(float(row['ymin']) / height)
        ymaxs.append(float(row['ymax']) / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(category_idx[row['class']])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def gen_tfrecord(path_to_images, path_to_annot, path_to_label_map, path_to_save_tfrecords):

    csv_path = path_to_annot
    images_path = path_to_images
    print("images path : ", images_path)
    print("csv path : ", csv_path)
    print("path to output tfrecords : ", path_to_save_tfrecords)
    label_map_dict = label_map_util.get_label_map_dict(path_to_label_map)
    writer = tf.io.TFRecordWriter(path_to_save_tfrecords)

    examples = pd.read_csv(csv_path)
    print("Generating tfrecord .... ")
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, images_path, label_map_dict)
        writer.write(tf_example.SerializeToString())

    writer.close()
    print('Successfully created the TFRecords: {}'.format(path_to_save_tfrecords))
