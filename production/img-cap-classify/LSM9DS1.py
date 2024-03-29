from smbus import SMBus
import threading

OUT_X_L_XL = 0x28
OUT_X_H_XL = 0x29
OUT_Y_L_XL = 0x2A
OUT_Y_H_XL = 0x2B
OUT_Z_L_XL = 0x2C
OUT_Z_H_XL = 0x2D
CTRL_REG6_XL = 0x20


class LSM9DS1(object):
  """Watches an LSM9DS1 to see if it is moving or not"""

  def __init__(self, bus_num=1, address=0x6b):
    super(LSM9DS1, self).__init__()
    self.bus_num = bus_num
    self.address = address
    self.bus = SMBus(self.bus_num)
    self.setup()

    self.curr_x = 0.0
    self.prev_x = 0.0
    self.curr_y = 0.0
    self.prev_x = 0.0
    self.curr_z = 0.0
    self.prev_z = 0.0
    self.curr_d = 0.0
    self.prev_d = 0.0
    self.slow = 0.5
    self.thresh_start = 0.1
    self.thresh_stop = 0.0005
    self.prev_moving = False
    self.curr_moving = False
    self.running = threading.Event()
    self.thread = None
    self.start_actions = {}
    self.stop_actions = {}
    self.loop_actions = {}
    self.start_time = None

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.stop()

  def setup(self):
    #  enable accelerometer @ 50hz
    self.bus.write_byte_data(self.address, CTRL_REG6_XL, 0x40)

  def read_i2c_word(self, register):
    low = self.bus.read_byte_data(self.address, register)
    high = self.bus.read_byte_data(self.address, register + 1)

    value = (high << 8) + low

    if (value >= 0x8000):
      value = -((65535 - value) + 1)

    return value / 32768.0

  def get_v(self, reg):
    return round(self.read_i2c_word(reg), 3)

  def get_x(self):
    return self.get_v(OUT_X_L_XL)

  def get_y(self):
    return self.get_v(OUT_Y_L_XL)

  def get_z(self):
    return self.get_v(OUT_Z_L_XL)

  def add_start_action(self, key, func):
    self.start_actions[key] = func

  def remove_start_action(self, key):
    del self.start_actions[key]

  def add_stop_action(self, key, func):
    self.stop_actions[key] = func

  def remove_stop_action(self, key):
    del self.stop_actions[key]

  def add_loop_action(self, key, func):
    self.loop_actions[key] = func

  def remove_loop_action(self, key):
    del self.loop_actions[key]

  def start(self):
    self.stop()
    self.running.set()
    self.thread = threading.Thread(target=self.loop)
    self.thread.start()

  def stop(self):
    self.running.clear()
    if self.thread is not None:
      self.thread.join()

  def loop(self):
    while self.running.is_set():
      # store previous values
      self.prev_x = self.curr_x
      self.prev_y = self.curr_y
      self.prev_z = self.curr_z
      self.prev_d = self.curr_d
      self.prev_moving = self.curr_moving

      # get new values
      self.curr_x = self.get_x()
      self.curr_y = self.get_y()
      self.curr_z = self.get_z()

      # calculate the amount of change
      dx = abs(self.curr_x - self.prev_x)
      dy = abs(self.curr_y - self.prev_y)
      dz = abs(self.curr_z - self.prev_z)

      # get total change
      self.curr_d = dx + dy + dz
      # filter total change
      self.curr_d = (self.curr_d * self.slow) + (self.prev_d * (1.0 - self.slow))

      # decide if moving
      thresh = self.thresh_stop if self.curr_moving else self.thresh_start
      self.curr_moving = self.curr_d > thresh

      if self.curr_moving and not self.prev_moving:
        for k, func in self.start_actions.items():
          func()
      elif not self.curr_moving and self.prev_moving:
        for k, func in self.stop_actions.items():
          func()

      for k, func in self.loop_actions.items():
        func(self.curr_moving)

      self.running.wait(0.05)
