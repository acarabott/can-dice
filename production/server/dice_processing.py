from PIL import Image


def crop_dice(img_file):
  try:
    img = Image.open(img_file)
  except IOError as e:
    print("couldn't read image")
    raise

  dim = 500
  y_start = 112
  y_end = y_start + dim
  x_starts = [0, 534, 1125]

  crop_boxes = [(x, y_start, x + dim, y_end) for x in x_starts]
  crops = [img.crop(box) for box in crop_boxes]
  return crops
