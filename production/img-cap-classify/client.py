from DiceCam import DiceCam
from LSM9DS1 import LSM9DS1

import requests
import time
import tempfile
import argparse


def capture_and_post_factory(cam, server_url):
  def capture_and_post():
    print('capturing at {}'.format(time.asctime()))
    with tempfile.TemporaryFile() as img:
      cam.capture(img)
      img.seek(0)
      files = {'img': ('img.jpg', img)}
      try:
        r = requests.post(server_url, files=files)
        print(r.text)
      except requests.ConnectionError:
        print("connection error")

  return capture_and_post


def main(server_url):
  print("started camera client")
  with DiceCam(12, 13, 18) as cam, LSM9DS1(1, 0x6b) as accel:
    accel.add_stop_action('capture', capture_and_post_factory(cam, server_url))
    while True:
      time.sleep(0.05)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('server_url', help='url to post images to', type=str)
  args = parser.parse_args()

  main(args.server_url)
