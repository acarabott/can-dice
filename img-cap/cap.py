#!/usr/bin/env python3

import os
import subprocess
import RPi.GPIO as GPIO
import time
import glob

filelist = glob.glob('output/*.jpg')
for f in filelist:
  os.remove(f)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led_pin = 18
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.HIGH)

prefix = 'dice-'

# biggest = max([int(os.path.splitext(img)[0].replace(prefix, '') for img in imgs])
# next_name = prefix + str(biggest + 1).zfill(3) + '.jpg'
next_name = 'test.jpg'

opts = range(6000, 60000, 1000) 
opts = [25000]
for opt in opts:
  opt = str(opt)
  print(opt)
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
  #  '--contrast', '100',
  #  '--brightness', '100',
    '-o', 'output/' + next_name])

GPIO.output(18, GPIO.LOW)

GPIO.cleanup()
