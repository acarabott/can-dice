import subprocess
import RPi.GPIO as GPIO


class DiceCam():
  """Dice Cam! Flash the LEDs, take a pic!"""

  def __init__(self, *led_pins):
    super(DiceCam, self).__init__()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    self.led_pins = [*led_pins]
    self.setup_leds()

  def setup_leds(self):
    for pin in self.led_pins:
      GPIO.setup(pin, GPIO.OUT)

  def set_leds(self, value):
    for pin in self.led_pins:
      GPIO.output(pin, value)

  def leds_on(self):
    self.set_leds(GPIO.HIGH)

  def leds_off(self):
    self.set_leds(GPIO.LOW)

  def capture(self, out_path):
    self.leds_on()
    subprocess.call(['raspistill',
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
                     '-o', out_path])
    self.leds_off()

  def cleanup(self):
    self.leds_off()
    GPIO.cleanup()
