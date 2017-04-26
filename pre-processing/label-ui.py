#!/usr/bin/env python3

# - show prev image, cur image and 5 after
# - on number input move image to target directory
# - on 'b' undo the previous move
# - on space skip image

import glob
import cv2
import shutil
import numpy as np

input_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/04-processing/'
todo_dir = input_dir + 'todo'
trash_dir = input_dir + 'done'
output_dir = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05-labelled/'

files = glob.glob('{}/*.jpg'.format(todo_dir))

values = dict()
processed = dict()

chunk_size = 5
idx = 0


def get_files():
  global idx
  c_idx = idx - (idx % chunk_size)
  return files[c_idx:c_idx + chunk_size]


def move(dst, value):
  global idx
  file = files[idx]
  # shutil.move(file, dst)
  values[files[idx]] = value
  processed[file] = dst
  idx += 1


def label(label):
  move(output_dir + label, label)


def done():
  move(trash_dir, '-')


def undo():
  global idx
  idx = max(idx -1, 0)
  file = files[idx]
  # shutil.move(processed[file], todo_dir)
  # del processed[file]


cv2.namedWindow('labeller', cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)

running = True
escape = 27
while running:
  key = cv2.waitKey(60) & 0xFF

  img = np.zeros((700, 1500, 3), np.uint8)

  for i, file in enumerate(get_files()):
    dice = cv2.imread(file)
    big = cv2.resize(dice, (200, 200))

    xs = 20 + (i * (big.shape[0] + 20))
    xe = xs + big.shape[1]
    ys = 20
    ye = ys + big.shape[0]

    is_current = i == idx % chunk_size
    blue = (212, 156, 43)

    if is_current:
      img[ys - 10:ye + 10, xs - 10:xe + 10] = blue

    img[ys:ye, xs:xe] = big

    if file in values.keys():
      color = blue if is_current else (255, 255, 255)
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
    done()
  if key == ord('b'):
    undo()

  running = key != escape

cv2.destroyAllWindows()
# for f in filelist:
#  os.remove(f)

# filelist = glob.glob('{}/*.{}'.format(out_dir, file_format))
# for f in filelist:
#  os.remove(f)

# filelist = glob.glob('{}/*.{}'.format(out_dir, file_format))
# for f in filelist:
#  os.remove(f)

# imgs = glob.glob('{}/*.{}'.format(out_dir, ext))

# if len(imgs) == 0:
#   next_num = 0
# else:
#   nums = [int(splitext(basename(img))[0].replace(prefix, '')) for img in imgs]
#   next_num = 1 + max(nums)
