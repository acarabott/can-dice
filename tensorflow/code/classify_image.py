# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Simple image classification with Inception.

Run image classification with Inception trained on ImageNet 2012 Challenge data
set.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

Change the --image_file argument to any jpg image to compute a
classification of that image.

Please see the tutorial and website for a detailed description of how
to use this script to perform image recognition.

https://tensorflow.org/tutorials/image_recognition/

Modified by Arthur Carabott 2017
"""

import argparse
import numpy as np
import tensorflow as tf

lookup = None
sess = None
softmax_tensor = None


def create_graph(graph_path):
  with tf.gfile.FastGFile(graph_path, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    tf.import_graph_def(graph_def, name='')


def create_lookup(lookup_path):
  if not tf.gfile.Exists(lookup_path):
    tf.logging.fatal('lookup file does not exist %s', lookup_path)

  lines = tf.gfile.GFile(lookup_path).readlines()
  return [int(l.replace('\n', '')) for l in lines]


def run(image):
  global sess, softmax_tensor, lookup

  if not tf.gfile.Exists(image):
    tf.logging.fatal('File does not exist %s', image)
  image_data = tf.gfile.FastGFile(image, 'rb').read()

  predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
  predictions = np.squeeze(predictions)

  top = predictions.argsort()[-1]
  return (lookup[top], predictions[top])


def setup(model_dir):
  global sess
  if sess is not None:
    cleanup()

  create_graph('{}/output_graph.pb'.format(model_dir))

  global lookup
  lookup = create_lookup('{}/output_labels.txt'.format(model_dir))

  sess = tf.Session()

  global softmax_tensor
  softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')


def cleanup():
  global lookup, sess, softmax_tensor
  sess.close()
  sess = None
  lookup = None
  softmax_tensor = None


def main(model_dir, image_file):
  setup(model_dir)
  result = run(image_file)
  print(result)
  cleanup()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'model_dir',
      type=str,
      help="path to model (.pb file) and labels (.txt)")

  parser.add_argument(
      'image_file',
      type=str,
      help='Absolute path to image file.'
  )

  args, unparsed = parser.parse_known_args()
  main(args.model_dir, args.image_file)
