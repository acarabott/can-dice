#!/usr/bin/env python3

import glob
import cv2
import shutil
import numpy as np
from os.path import basename
import time


input_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/04-processing/'
todo_dir = input_dir + 'todo'
skip_dir = input_dir + 'skip'
output_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05-labelled/'

files = glob.glob('{}/*.jpg'.format(todo_dir))

values = dict()
processed = dict()

chunk_size = 6
idx = 0

blue = (212, 156, 43)
white = (255, 255, 255)
black = (0, 0, 0)


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
  return cv2.resize(dice, (150, 150))


cv2.namedWindow('labeller', cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)
running = True
escape = 27

start = time.time()

while running:
  key = cv2.waitKey(60) & 0xFF

  img = np.zeros((700, 1050, 3), np.uint8)
  img[0:img.shape[0], 0:img.shape[1]] = white

  prev_file = get_prev_file()
  cur_files = get_files()

  # draw last image from prev batch
  if prev_file is not None:
    big = get_img(prev_file)
    ys = 300
    ye = ys + big.shape[1]
    xs = 20
    xe = xs + big.shape[0]
    img[ys:ye, xs:xe] = big
    cv2.putText(img, values[prev_file], (xs + 25, ye + 150), 0, 5, white)

  # draw images in current batch
  for i, file in enumerate(get_files()):
    big = get_img(file)
    x_offset = 20

    xs = x_offset + (i * (big.shape[0] + 20))
    xe = xs + big.shape[1]
    ys = 20
    ye = ys + big.shape[0]

    is_current = i == idx % chunk_size

    # border
    border_w = 5 if is_current else 1
    color = blue if is_current else black
    img[ys - border_w:ye + border_w, xs - border_w:xe + border_w] = color

    # image
    img[ys:ye, xs:xe] = big

    # text
    if file in values.keys():
      color = blue if is_current else black
      cv2.putText(img, values[file], (xs + 25, ye + 150), 0, 5, color)

  # stats
  running_time = time.time() - start
  mins = running_time / 60.0
  per_min = idx / mins

  text_x = int(img.shape[1] / 2)
  cv2.putText(img, 'count: {}'.format(idx), (text_x, 450), 0, 2, blue)
  cv2.putText(img, 'time: {:.1f}'.format(running_time), (text_x, 520), 0, 2, black)
  cv2.putText(img, '{:.1f} / min'.format(per_min), (text_x, 590), 0, 2, black)

  # render
  cv2.imshow('labeller', img)

  # input handling
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
