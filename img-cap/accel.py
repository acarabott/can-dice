#!/usr/bin/env python3

import smbus

bus = smbus.SMBus(1)
address = 0x6b

OUT_X_L_XL = 0x28
OUT_X_H_XL = 0x29
OUT_Y_L_XL = 0x2A
OUT_Y_H_XL = 0x2B
OUT_Z_L_XL = 0x2C
OUT_Z_H_XL = 0x2D

bus.write_byte_data(address, 0x10, 0xfb)  # enable accell and gyro
bus.read_byte_data(address, OUT_X_L_XL) # read gyro x
