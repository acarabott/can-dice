#!/usr/bin/env python3

import argparse
import glob
import crop
import segment

in_path = None
out_dir = None
debug = False
file_ext = 'png'


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('action', help='"crop" or "segment"', type=str)
  parser.add_argument('in_path', help='glob for input images', type=str)
  parser.add_argument('out_dir', help='directory to output results', type=str)
  parser.add_argument('threshold', help='threshold see relevant file', type=int)
  parser.add_argument('--resize', help='whether to resize or not', type=bool)
  parser.add_argument('--file_ext', help='output file extension', type=str,
                      default='jpg')
  args = parser.parse_args()

  imgs = glob.glob('{}'.format(args.in_path))
  print(len(imgs))

  for i, img in enumerate(imgs):
    pargs = [img, args.out_dir, args.file_ext, args.threshold, args.resize]

    if args.action == 'crop':
      crop.process(*pargs)
    elif args.action == 'segment':
      segment.process(*pargs)

    if i % 100 == 0:
      print("processing: {}/{}".format(i, len(imgs)))


if __name__ == '__main__':
  main()
