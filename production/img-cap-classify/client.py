from DiceCam import DiceCam
from LSM9DS1 import LSM9DS1

import requests
import time
import tempfile

SERVER_URL = 'http://localhost:5000/classify'

cam = DiceCam(12, 13, 18)
accel = LSM9DS1(1, 0x6b)
running = True


def capture_and_post_factory(cam):
  def capture_and_post():
    print('capturing at {}'.format(time.asctime()))
    with tempfile.TemporaryFile() as img:
      cam.capture(img)
      files = {'img': img}
      r = requests.post(SERVER_URL, files=files)
      print(r.text)

  return capture_and_post


def main():
  with DiceCam(12, 13, 18) as cam, LSM9DS1(1, 0x6) as accel:
    accel.add_stop_action('capture', capture_and_post_factory(cam))
    while running:
      time.sleep(0.05)


if __name__ == '__main__':
  main()
