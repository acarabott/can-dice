#!/usr/bin/env python3

import os
from os.path import splitext, basename
import subprocess
import RPi.GPIO as GPIO
import time
import glob

out_dir = 'output'
prefix = 'dice-'

file_format = 'jpg'
imgs = glob.glob('{}/*.{}'.format(out_dir, file_format))


if len(imgs) == 0:
  next_num = 0
else:
  nums = [int(splitext(basename(img))[0].replace(prefix, '')) for img in imgs]
  next_num = 1 + max(nums)

out_name = '{}/{}{}.{}'.format(out_dir, prefix, str(next_num).zfill(4), file_format)

#filelist = glob.glob('{}/*.{}'.format(out_dir, file_format))
#for f in filelist:
#  os.remove(f)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led_pin = 18
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.HIGH)

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

GPIO.output(18, GPIO.LOW)
GPIO.cleanup()
