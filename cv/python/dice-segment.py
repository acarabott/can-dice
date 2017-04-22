#!/usr/bin/env python3

import numpy as np
import cv2
import os
import argparse


def get_output_path(in_path, out_dir, idx):
  prefix = os.path.splitext(os.path.basename(in_path))[0]
  return '{}/{}-{}.png'.format(out_dir, prefix, str(idx).zfill(2))


def write_img(img, path):
  cv2.imwrite(path, img)
  print('wrote to {}'.format(path))


def process_contour(contour, img):
  # dice min area (rotated rect)
  rect_min_area = cv2.minAreaRect(contour)
  rect_min_points = cv2.boxPoints(rect_min_area)

  # bounding rect of the *min area rect*
  rrb = cv2.boundingRect(rect_min_points)
  rrb_tl = rrb[0:2]
  rrb_br = tuple([sum(x) for x in zip(rrb_tl, rrb[2:4])])

  # crop to bounding rect
  cropped = img[rrb_tl[1]:rrb_br[1], rrb_tl[0]:rrb_br[0]]

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
  straight = cv2.warpAffine(cropped, matrix, dsize)

  # crop based on nonzero values
  nonzero = straight.nonzero()
  y_start = min(nonzero[0])
  y_end = max(nonzero[0])
  x_start = min(nonzero[1])
  x_end = max(nonzero[1])
  straight_crop = straight[y_start:y_end, x_start:x_end]

  # put into square box
  s = straight_crop.shape[0:2]
  max_dim = max(s)
  x_start = int((max_dim - s[0]) / 2)
  x_end = x_start + s[0]
  y_start = int((max_dim - s[1]) / 2)
  y_end = y_start + s[1]

  square = np.zeros((max_dim, max_dim))
  square[x_start:x_end, y_start:y_end] = straight_crop

  # resize
  small = cv2.resize(square, (40, 40))

  return small


def get_segmented(img):
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  blurred = cv2.blur(img_gray, (20, 20))

  # white dice on black
#     retval, threshold = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
  # black dice on white
  retval, threshold = cv2.threshold(blurred, 70, 255, cv2.THRESH_BINARY_INV)

  min_idx = img.shape.index(min(img.shape[0:2]))
  max_idx = abs(1 - min_idx)
  ratio = img.shape[min_idx] / img.shape[max_idx]
  dim = 200
  size = (dim, int(dim * ratio))
  resized = cv2.resize(threshold, size)

  resized, contours, hierarchy = cv2.findContours(resized,
                                                  cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_NONE)

  return [process_contour(c, resized) for c in contours]


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('in_path', help='path to input image', type=str)
  parser.add_argument('--out_dir', help='directory to output results',
                      type=str, default='.')
  args = parser.parse_args()

  img = cv2.imread(args.in_path)
  if img is None:
    print("couldn't read image")
    return

  for i, segment in enumerate(get_segmented(img)):
    filename = get_output_path(args.in_path, args.out_dir, i)
    write_img(segment, filename)


if __name__ == '__main__':
  main()
