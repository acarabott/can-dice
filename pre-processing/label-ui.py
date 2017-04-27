#!/usr/bin/env python3

import glob
import cv2
import shutil
import numpy as np
from os.path import basename
import time
from PIL import Image, ImageFont, ImageDraw

# use a truetype font
font_small = ImageFont.truetype("/Users/ac/Library/Fonts/Lato-Light.ttf", 40)
font_large = ImageFont.truetype("/Users/ac/Library/Fonts/Lato-Light.ttf", 100)

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


def get_img(path, shape):
  real_path = processed[path] if path in processed.keys() else path
  dice = cv2.imread(real_path)
  return cv2.resize(dice, shape)


# returns a new image!
# textargs is a list of dicts with origin, text, font, fill
def add_text(img, textargs):
  pil_img = Image.fromarray(img, 'RGB')
  draw = ImageDraw.Draw(pil_img)
  for args in textargs:
    draw.text(args['origin'], args['text'], font=args['font'], fill=args['fill'])
  return np.array(pil_img)


# returns a new canvas
def draw_image(canvas, img, xs, xe, ys, ye, border_w, text, color):
  # border
  yslice = slice(max(0, ys - border_w), min(ye + border_w, canvas.shape[0]))
  xslice = slice(max(0, xs - border_w), min(xe + border_w, canvas.shape[1]))
  canvas[yslice, xslice] = color

  # image
  canvas[ys:ye, xs:xe] = img

  # text
  canvas = add_text(canvas, [{'origin': (xs + 25, ye + 25),
                              'text': text,
                              'font': font_large,
                              'fill': color}])

  return canvas


cv2.namedWindow('labeller', cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)
running = True
escape = 27

start = time.time()

while running:
  key = cv2.waitKey(60) & 0xFF

  width = 800
  # height = int(width * (9 / 16))
  height = 500
  img = np.zeros((height, width, 3), np.uint8)
  img[0:img.shape[0], 0:img.shape[1]] = white

  prev_file = get_prev_file()
  cur_files = get_files()

  margin = int(width * 0.04)
  dice_shape = int(img.shape[1] / (chunk_size + 2))
  dice_shape = (dice_shape, dice_shape)

  # draw last image from prev batch
  if prev_file is not None:
    dice = get_img(prev_file, dice_shape)
    ys = int(img.shape[1] * 0.3)
    ye = ys + dice.shape[1]
    xs = int(margin / 2)
    xe = xs + dice.shape[0]
    img = draw_image(img, dice, xs, xe, ys, ye, 1, values[prev_file], black)

  # draw images in current batch
  for i, file in enumerate(get_files()):
    dice = get_img(file, dice_shape)

    print(margin)
    xs = int(margin / 2) + int(i * (dice.shape[1] + margin))
    xe = xs + dice.shape[1]
    ys = margin
    ye = ys + dice.shape[0]

    is_current = i == idx % chunk_size

    border_w = 5 if is_current else 1
    color = blue if is_current else black
    text = values[file] if file in values.keys() else ''
    img = draw_image(img, dice, xs, xe, ys, ye, border_w, text, color)

  # stats
  running_time = time.time() - start
  mins = running_time / 60.0
  per_min = idx / mins

  pil_img = Image.fromarray(img, 'RGB')
  draw = ImageDraw.Draw(pil_img)

  text_x = int(img.shape[1] * 0.75)
  text_y = int(img.shape[0] * 0.6)
  stats = [{'origin': (text_x, text_y + 0),
            'text': 'count: {}'.format(idx),
            'fill': blue,
            'font': font_small},
           {'origin': (text_x, text_y + 50),
            'text': 'time: {:.1f}'.format(running_time),
            'fill': black,
            'font': font_small},
           {'origin': (text_x, text_y + 100),
            'text': '{:.1f} / min'.format(per_min),
            'fill': black,
            'font': font_small}]

  img = add_text(img, stats)

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
