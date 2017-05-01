#!/usr/bin/env python3

import glob
from os.path import getsize
import shutil
import argparse


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('in_dir', help='path to input directory', type=str)
  parser.add_argument('out_dir', help='directory to output results', type=str)
  parser.add_argument('--thresh', help='file size threshold (bytes), only keep files >=',
                      type=int, default=1600)
  args = parser.parse_args()

  for i, file in enumerate(glob.glob('{}/*'.format(args.in_dir))):
    if getsize(file) >= args.thresh:
      new_name = '{}.jpg'.format(str(i).zfill(5))
      path = '{}/{}'.format(args.out_dir, new_name)
      shutil.copyfile(file, path)


if __name__ == '__main__':
  main()
