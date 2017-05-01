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
  print('wrote to {}'.format(path))


def write_segment_img(img, out_dir, file_ext):
  path = get_output_path(out_dir, file_ext)
  write_img(img, path)


def write_debug_img(img, key):
  global debug_dir
  path = '{}/{}.png'.format(debug_dir, key)
  write_img(img, path)


def process_contour(contour, img):
  area_contour = cv2.contourArea(contour)
  area_img = img.shape[0] * img.shape[1]
  area_ratio = area_contour / area_img

  if area_ratio < 0.1:
    return None

  # dice min area (rotated rect)
  rect_min_area = cv2.minAreaRect(contour)
  rect_min_points = cv2.boxPoints(rect_min_area)

  # bounding rect of the *min area rect*
  rrb = cv2.boundingRect(rect_min_points)
  rrb_tl = rrb[0:2]
  rrb_br = tuple([sum(x) for x in zip(rrb_tl, rrb[2:4])])

  # crop to bounding rect
  cropped = img[rrb_tl[1]:rrb_br[1], rrb_tl[0]:rrb_br[0]]
  if debug:
    write_debug_img(cropped, 'cropped')

  # straighten image
  angle = rect_min_area[2]
  keep = angle > -45.  # if the angle is less than -45 we need to swap w/h

  rrb_width = rrb_br[0] - rrb_tl[0]
  rrb_height = rrb_br[1] - rrb_tl[1]
  width = rrb_width if keep else rrb_height
  height = rrb_height if keep else rrb_width
  angle += (0 if keep else 90)
  center = (width / 2, height / 2)
  dsize = (width, height)
  matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

  if 0 in cropped.shape:
    return None

  straight = cv2.warpAffine(cropped, matrix, dsize)
  if debug:
    write_debug_img(straight, 'straight')

  # crop based on nonzero values
  nonzero = straight.nonzero()
  if len(nonzero[0]) == 0 or len(nonzero[1]) == 0:
    return None

  y_start = min(nonzero[0])
  y_end = max(nonzero[0])
  x_start = min(nonzero[1])
  x_end = max(nonzero[1])
  straight_crop = straight[y_start:y_end, x_start:x_end]
  if debug:
    write_debug_img(straight_crop, 'straight_crop')

  square = np.zeros(img.shape[0:2])
  y_len = y_end - y_start
  x_len = x_end - x_start
  y_start_sq = int((square.shape[0] - y_len) / 2)
  y_end_sq = y_start_sq + y_len
  x_start_sq = int((square.shape[1] - x_len) / 2)
  x_end_sq = x_start_sq + x_len

  square[y_start_sq:y_end_sq, x_start_sq:x_end_sq] = straight_crop
  if debug:
    write_debug_img(square, 'square')

  if 0 in square.shape:
    return

  return square


def get_segmented(img, threshold):
  global debug

  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  if debug:
    write_debug_img(img_gray, '01-gray')

  blur_size = (img_gray.shape[0], img_gray.shape[1])
  coeff = 0.012
  blur_size = tuple([max(1, int(d * coeff)) for d in img_gray.shape[0:2]])
  blurred = cv2.blur(img_gray, blur_size)
  if debug:
    write_debug_img(blurred, '02-blurred')

  # white dice on black
#     retval, threshold = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
  # black dice on white
  retval, threshold = cv2.threshold(blurred, threshold, 255,
                                    cv2.THRESH_BINARY_INV)
  if debug:
    write_debug_img(threshold, '03-threshold')

  threshold, contours, hierarchy = cv2.findContours(threshold,
                                                    cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_NONE)
  if debug:
    cimg = np.zeros(threshold.shape)
    cv2.drawContours(cimg, contours, -1, 255)
    write_debug_img(cimg, '04-contours')

  processed = [process_contour(c, threshold) for c in contours]
  return [p for p in processed if p is not None]


def process(in_path, out_dir, file_ext, threshold=127):
  img = cv2.imread(in_path)
  if img is None:
    print("couldn't read image: {}".format())
    return

  for i, segment in enumerate(get_segmented(img, threshold)):
    write_segment_img(segment, out_dir, file_ext)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('in_path', help='path to input image', type=str)
  parser.add_argument('out_dir', help='directory to output results', type=str)
  parser.add_argument('--ext', help='output file extension', type=str,
                      default='png')
  parser.add_argument('--threshold', help='threshold 0-255', type=int,
                      default=160)
  parser.add_argument('--debug', help='if True then output debug images',
                      type=bool, default=False)
  parser.add_argument('--debug_dir', help='output dir for debug images',
                      type=str, default='.')
  args = parser.parse_args()

  global debug, debug_dir
  debug = args.debug
  debug_dir = args.debug_dir

  process(args.in_path, args.out_dir, args.ext, args.threshold, args.resize)


if __name__ == '__main__':
  main()
