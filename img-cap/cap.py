#!/usr/bin/env python3

import os
from os.path import splitext, basename
import subprocess
import RPi.GPIO as GPIO
import time
import glob

#filelist = glob.glob('{}/*.{}'.format(out_dir, file_format))
#for f in filelist:
#  os.remove(f)

def get_file_name(img_count):
  out_dir = 'output'
  prefix = 'dice-'

  file_format = 'jpg'
  imgs = glob.glob('{}/*.{}'.format(out_dir, file_format))

  # if len(imgs) == 0:
  #   next_num = 0
  # else:
  #   nums = [int(splitext(basename(img))[0].replace(prefix, '')) for img in imgs]
  #   next_num = 1 + max(nums)
  next_num = img_count
  return '{}/{}{}.{}'.format(out_dir, prefix, str(next_num).zfill(5), file_format)



def capture(img_count):
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  led_pins= [13, 12, 18]

  for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

  out_name = get_file_name(img_count)

  subprocess.call([
    'raspistill',
    '--nopreview',
    '-w', '1640',
    '-h', '922',
    '-t', '1',
    '-ex', 'verylong',
    '-cfx', '128:128',
    '-awb', 'fluorescent',
    '-mm', 'spot',
    '-ISO', '800',
    '--shutter', '25000',
    '--contrast', '90',
    '--brightness', '30',
    '-o', out_name])

  print(out_name)

  for pin in led_pins:
    GPIO.output(pin, GPIO.LOW)

  GPIO.cleanup()
