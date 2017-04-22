import numpy as np
import cv2
import os

paths = ['ten-3.png']


for i, path in enumerate(paths):

  img = cv2.imread('../imgs/{}'.format(path))
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  blurred = cv2.blur(img_gray, (20, 20))

  # white dice on black
#     retval, threshold = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
  # black dice on white
  retval, threshold = cv2.threshold(img_gray, 70, 255, cv2.THRESH_BINARY_INV)

  min_idx = img.shape.index(min(img.shape[0:2]))
  max_idx = abs(1 - min_idx)
  ratio = img.shape[min_idx] / img.shape[max_idx]
  dim = 200
  size = (dim, int(dim * ratio))
  resized = cv2.resize(threshold, size)

  resized, contours, hierarchy = cv2.findContours(resized,
                                                  cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_NONE)

  for cidx, contour in enumerate(contours):
    # dice min area (rotated rect)
    rect_min_area = cv2.minAreaRect(contour)
    rect_min_points = cv2.boxPoints(rect_min_area)

    # bounding rect of the *min area rect*
    rrb = cv2.boundingRect(rect_min_points)
    rrb_tl = rrb[0:2]
    rrb_br = tuple([sum(x) for x in zip(rrb_tl, rrb[2:4])])
    rrb_center = (rrb_tl[0] + rrb[2] / 2, rrb_tl[1] + rrb[3] / 2)

    # crop to bounding rect
    cropped = resized[rrb_tl[1]:rrb_br[1], rrb_tl[0]:rrb_br[0]]

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
    min_dim = min(s)
    x_start = int((max_dim - s[0]) / 2)
    x_end = x_start + s[0]
    y_start = int((max_dim - s[1]) / 2)
    y_end = y_start + s[1]

    square = np.zeros((max_dim, max_dim))
    square[x_start:x_end, y_start:y_end] = straight_crop

    # resize
    small = cv2.resize(square, (40, 40))

    # write to file
    prefix = os.path.splitext(path)[0]
    filename = 'output/{}-{}.png'.format(prefix, str(cidx).zfill(2))
    cv2.imwrite(filename, small)
    print('wrote to {}'.format(filename))
