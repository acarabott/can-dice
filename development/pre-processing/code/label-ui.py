#!/usr/bin/env python3

import glob
import cv2
import shutil
import numpy as np
from os.path import basename
import time
from PIL import Image, ImageFont, ImageDraw

# use a truetype font
font_label = ImageFont.truetype("/Users/ac/Library/Fonts/Lato-Light.ttf", 35)
font_stats = ImageFont.truetype("/Users/ac/Library/Fonts/Lato-Light.ttf", 25)

input_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/04-processing/'
todo_dir = input_dir + 'todo'
skip_dir = input_dir + 'skip'
output_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05-labelled/'

files = glob.glob('{}/*.jpg'.format(todo_dir))

values = dict()
processed = dict()

chunk_size = 12
line_size = int(chunk_size / 2)
idx = 0

blue = (212, 156, 43)
white = (255, 255, 255)
black = (0, 0, 0)

start = time.time()
timer_start = time.time()
timer_dur = 60.0
hist = []
peak = 0


def get_chunk_idx():
  global idx, chunk_size
  return idx - (idx % chunk_size)


def get_files():
  global idx, chunk_size
  c_idx = get_chunk_idx()

  if idx % chunk_size < line_size:
    return files[c_idx:c_idx + chunk_size]
  else:
    bottom_start = c_idx + line_size
    bottom_end = bottom_start + line_size
    bottom_row = files[bottom_start:bottom_end]
    top_row = files[bottom_end:bottom_end + line_size]
    return top_row + bottom_row

  return None


def get_prev_file():
  global idx
  if idx % line_size == 0 and idx != 0:
    return files[idx - 1]


def move(dst, value):
  global idx, hist, peak
  file = files[idx]
  shutil.move(file, dst)
  values[files[idx]] = value
  processed[file] = '{}/{}'.format(dst, basename(file))
  idx += 1
  hist.append(time.time())
  hist = [t for t in hist if t >= time.time() - timer_dur]
  peak = max(peak, len(hist))


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
  canvas = add_text(canvas, [{'origin': (xs + 35, ye + 5),
                              'text': text,
                              'font': font_label,
                              'fill': color}])

  return canvas


def draw_files(img, files, dice_shape):
  for i, file in enumerate(files):
    dice = get_img(file, dice_shape)

    if i % chunk_size < line_size:
      xs = int(margin / 2) + int(i * (dice_shape[1] + margin))
      xe = xs + dice_shape[1]
      ys = margin
      ye = ys + dice_shape[0]
    else:
      xe = img.shape[1] - int(margin * 0.75) - int((i % line_size) * (dice.shape[1] + margin))
      xs = xe - dice_shape[1]
      ys = margin + dice_shape[0] + margin * 2
      ye = ys + dice_shape[0]

    global idx
    is_current = i == idx % chunk_size

    border_w = 5 if is_current else 1
    color = blue if is_current else black
    text = values[file] if file in values.keys() else ''
    img = draw_image(img, dice, xs, xe, ys, ye, border_w, text, color)

  return img


cv2.namedWindow('Dice Labeller', cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)
running = True
escape = 27

while running:
  key = cv2.waitKey(60) & 0xFF

  width = 800
  # height = int(width * (9 / 16))
  height = 600
  img = np.zeros((height, width, 3), np.uint8)
  img[0:img.shape[0], 0:img.shape[1]] = white

  cur_files = get_files()

  margin = int(width * 0.04)
  dice_shape = int(img.shape[1] / (line_size + 2))
  dice_shape = (dice_shape, dice_shape)

  # draw images in current batch
  img = draw_files(img, get_files(), dice_shape)

  file = get_prev_file()
  if file is not None:
    xs = int(img.shape[1] / 2) - int(dice_shape[1] / 2)
    xe = xs + dice_shape[1]
    ys = int(img.shape[0] * 0.6)
    ye = ys + dice_shape[0]
    dice = get_img(file, dice_shape)
    text = values[file] if file in values.keys() else ''
    img = draw_image(img, dice, xs, xe, ys, ye, 1, text, black)

  # stats
  running_time = time.time() - start
  mins = running_time / 60.0
  avg = idx / mins

  pil_img = Image.fromarray(img, 'RGB')
  draw = ImageDraw.Draw(pil_img)

  def get_x(c):
    return int(img.shape[1] * c)

  text_y = int(img.shape[0] * 0.9)
  stats = [{'origin': (get_x(0.025), text_y),
            'text': 'count: {}'.format(idx),
            'fill': blue,
            'font': font_stats},
           {'origin': (get_x(0.225), text_y),
            'text': 'time: {:.1f}'.format(running_time),
            'fill': black,
            'font': font_stats},
           {'origin': (get_x(0.425), text_y),
            'text': 'avg: {:.1f} / min'.format(avg),
            'fill': black,
            'font': font_stats},
           {'origin': (get_x(0.725), text_y),
            'text': 'peak: {:.1f} / min'.format(peak),
            'fill': black,
            'font': font_stats}]

  img = add_text(img, stats)

  # render
  cv2.imshow('Dice Labeller', img)

  # input handling
  if key == ord('1') or key == ord('q'):
    label('1')
  if key == ord('2'):
    label('2')
  if key == ord('3'):
    label('3')
  if key == ord('4') or key == ord('r'):
    label('4')
  if key == ord('5') or key == ord('v'):
    label('5')
  if key == ord('6') or key == ord('b'):
    label('6')
  if key == ord('7') or key == ord('u'):
    label('7')
  if key == ord('8'):
    label('8')
  if key == ord('9'):
    label('9')
  if key == ord('0') or key == ord('p'):
    label('0')
  if key == ord(' '):
    undo()
  if key == 8:
    skip()


  running = key != escape

cv2.destroyAllWindows()
