#!/usr/bin/env python3

import numpy as np
import cv2
import argparse
import glob
from os.path import splitext, basename

debug = False
debug_dir = '.'


def get_output_path(out_dir, file_ext):
  imgs = glob.glob('{}/*.{}'.format(out_dir, file_ext))

  if len(imgs) == 0:
    next_num = 0
  else:
    nums = [int(splitext(basename(i))[0]) for i in imgs]
    next_num = 1 + max(nums)

  return '{}/{}.{}'.format(out_dir, str(next_num).zfill(5), file_ext)


def write_img(img, path):
  cv2.imwrite(path, img)


def write_segment_img(img, out_dir, file_ext):
  path = get_output_path(out_dir, file_ext)
  write_img(img, path)


def process(in_path, out_dir, file_ext, threshold=127):
  img = cv2.imread(in_path)
  if img is None:
    print("couldn't read image")
    return

  dim = 500
  y_start = 112
  y_end = y_start + dim
  x_starts = [0, 534, 1125]
  crop_dims = [[slice(y_start, y_end), slice(x, x + dim)] for x in x_starts]

  for dim in crop_dims:
    crop = img[dim[0], dim[1]]
    small = cv2.resize(crop, (50, 50))
    write_segment_img(small, out_dir, file_ext)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('in_path', help='path to input image', type=str)
  parser.add_argument('out_dir', help='directory to output results', type=str)
  parser.add_argument('--ext', help='output file extension', type=str,
                      default='jpg')
  parser.add_argument('--threshold', help='threshold 0-255', type=int,
                      default=127)
  parser.add_argument('--debug', help='if True then output debug images',
                      type=bool, default=False)
  parser.add_argument('--debug_dir', help='output dir for debug images',
                      type=str, default='.')
  args = parser.parse_args()

  global debug, debug_dir
  debug = args.debug
  debug_dir = args.debug_dir

  process(args.in_path, args.out_dir, args.ext, args.threshold)


if __name__ == '__main__':
  main()
