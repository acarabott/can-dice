import numpy as np
import tensorflow as tf


class Brain():
  """Image classification based on retrained Inception"""

  def __init__(self, model_path, labels_path):
    super(Brain, self).__init__()
    self.create_graph(model_path)
    self.lookup = self.create_lookup(labels_path)
    self.sess = tf.Session()
    self.softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.exit()

  def create_graph(self, model_path):
    with tf.gfile.FastGFile(model_path, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      tf.import_graph_def(graph_def, name='')

  def create_lookup(self, lookup_path):
    if not tf.gfile.Exists(lookup_path):
      tf.logging.fatal('lookup file does not exist %s', lookup_path)

    lines = tf.gfile.GFile(lookup_path).readlines()
    return [int(l.replace('\n', '')) for l in lines]

  def classify(self, image):
    if type(image) is str:
      if not tf.gfile.Exists(image):
        tf.logging.fatal('File does not exist %s', image)
      image = tf.gfile.FastGFile(image, 'rb').read()

    predictions = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': image})
    predictions = np.squeeze(predictions)

    top = predictions.argsort()[-1]
    return (self.lookup[top], predictions[top])

  def exit(self):
    self.sess.close()
