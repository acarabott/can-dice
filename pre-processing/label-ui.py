#!/usr/bin/env python3

# - show prev image, cur image and 5 after
# - on number input move image to target directory
# - on 'b' undo the previous move
# - on space skip image

import glob
import cv2
import shutil
import numpy as np
from os.path import basename

input_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/04-processing/'
todo_dir = input_dir + 'todo'
skip_dir = input_dir + 'skip'
output_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05-labelled/'

files = glob.glob('{}/*.jpg'.format(todo_dir))

values = dict()
processed = dict()

chunk_size = 5
idx = 0

blue = (212, 156, 43)
white = (255, 255, 255)


def get_chunk_idx():
  global idx, chunk_size
  return idx - (idx % chunk_size)


def get_files():
  global chunk_size
  c_idx = get_chunk_idx()
  return files[c_idx:c_idx + chunk_size]


def get_prev_file():
  global idx
  if idx % chunk_size == 0 and idx != 0:
    return files[idx - 1]

  return None


def move(dst, value):
  global idx
  file = files[idx]
  shutil.move(file, dst)
  values[files[idx]] = value
  processed[file] = '{}/{}'.format(dst, basename(file))
  idx += 1


def label(label):
  move(output_dir + label, label)


def skip():
  move(skip_dir, '-')


def undo():
  global idx
  if idx == 0:
    return
  idx = max(idx - 1, 0)
  file = files[idx]
  shutil.move(processed[file], todo_dir)
  del processed[file]


def get_img(path):
  real_path = processed[path] if path in processed.keys() else path
  dice = cv2.imread(real_path)
  return cv2.resize(dice, (200, 200))


cv2.namedWindow('labeller', cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)
running = True
escape = 27
while running:
  key = cv2.waitKey(60) & 0xFF

  img = np.zeros((700, 1500, 3), np.uint8)

  prev_file = get_prev_file()
  cur_files = get_files()

  if prev_file is not None:
    big = get_img(prev_file)
    ys = 20
    ye = ys + big.shape[1]
    xs = 20
    xe = xs + big.shape[0]
    img[ys:ye, xs:xe] = big
    cv2.putText(img, values[prev_file], (xs + 25, ye + 150), 0, 5, white)

  for i, file in enumerate(get_files()):
    big = get_img(file)
    x_offset = 280 + 20

    xs = x_offset + (i * (big.shape[0] + 20))
    xe = xs + big.shape[1]
    ys = 20
    ye = ys + big.shape[0]

    is_current = i == idx % chunk_size

    if is_current:
      img[ys - 10:ye + 10, xs - 10:xe + 10] = blue

    img[ys:ye, xs:xe] = big

    if file in values.keys():
      color = blue if is_current else white
      cv2.putText(img, values[file], (xs + 25, ye + 150), 0, 5, color)

  cv2.imshow('labeller', img)

  if key == ord('0'):
    label('0')
  if key == ord('1'):
    label('1')
  if key == ord('2'):
    label('2')
  if key == ord('3'):
    label('3')
  if key == ord('4'):
    label('4')
  if key == ord('5') or key == ord('f'):
    label('5')
  if key == ord('6') or key == ord('h'):
    label('6')
  if key == ord('7'):
    label('7')
  if key == ord('8'):
    label('8')
  if key == ord('9'):
    label('9')
  if key == ord(' '):
    skip()
  if key == ord('b') or key == 8:
    undo()

  running = key != escape

cv2.destroyAllWindows()
