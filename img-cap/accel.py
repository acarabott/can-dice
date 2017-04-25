#!/usr/bin/env python3

import smbus
import time
import cap

print("started accelerometer listener")

bus = smbus.SMBus(1)
address = 0x6b

OUT_X_L_XL = 0x28
OUT_X_H_XL = 0x29
OUT_Y_L_XL = 0x2A
OUT_Y_H_XL = 0x2B
OUT_Z_L_XL = 0x2C
OUT_Z_H_XL = 0x2D

def read_i2c_word(register):
  low = bus.read_byte_data(address, register)
  high = bus.read_byte_data(address, register + 1)
   
  value = (high << 8) + low

  if (value >= 0x8000):
    value = -((65535 - value) + 1)
  
  return value / 32768.0
 
#bus.write_byte_data(address, 0x10, 0xfb)  # enable accell and gyro
# Linear acceleration sensor control register 6
# enable accelerometer @ 50hx
# 0 1 0  0 0  0  0 0 = 0x40 
CTRL_REG6_XL = 0x20  
bus.write_byte_data(address, CTRL_REG6_XL, 0x40)

def getv(reg): 
  return round(read_i2c_word(reg), 3)

def getx():
  return getv(OUT_X_L_XL)

def gety():
  return getv(OUT_Y_L_XL)

def getz():
  return getv(OUT_Z_L_XL)

x = px = getx()
y = px = gety()
z = pz = getz()

d = pd = 0
moving = False

img_count = 0
while True:
  # store previous values
  px = x
  py = y
  pz = z
  pd = d

  # get new values
  x = getx() 
  y = gety() 
  z = getz() 
  
  # calculate the amount of change
  dx = (x - px) ** 2
  dy = (y - py) ** 2
  dz = (z - pz) ** 2
  
  # get total change, filtered  
  d = dx + dy + dz 
  m = 0.3 # 0.3 for hand
  m = 0.7 if d > pd else 0.3
  d = (d * m) + (pd * (1.0 - m))
  
  # decide if moving
  thresh = 0.1 # 0.05 for hand

  now_moving = d > thresh
  # print('{:04.2f}'.format(d), now_moving)
  # if now_moving and not moving:
  #   print("started VVVVVVV")
  #   print(d)

  if moving and not now_moving:
    if y > 0:
      cap.capture(img_count)
      img_count += 1
      print("snap!")
    #print("stopped -------")

  moving = now_moving
  time.sleep(0.05)

