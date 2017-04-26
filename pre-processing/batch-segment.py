#!/usr/bin/env python3

import argparse
import glob
import segment

in_path = None
out_dir = None
debug = False
file_ext = 'png'


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('in_path', help='path to input image', type=str)
  parser.add_argument('out_dir', help='directory to output results', type=str)
  parser.add_argument('--file_ext', help='output file extension', type=str,
                      default='jpg')
  args = parser.parse_args()

  imgs = glob.glob('{}/**/*'.format(args.in_path))

  for img in imgs:
    segment.process(img, args.out_dir, args.file_ext)


if __name__ == '__main__':
  main()
