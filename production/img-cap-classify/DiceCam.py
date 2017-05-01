import RPi.GPIO as GPIO
from picamera import PiCamera


class DiceCam(object):
  """Dice Cam! Flash the LEDs, take a pic!"""

  def __init__(self, *led_pins):
    super(DiceCam, self).__init__()
    self.led_pins = [*led_pins]
    self.camera = PiCamera()
    self.camera.resolution = (1640, 922)
    self.camera.iso = 800
    self.camera.awb_mode = 'fluorescent'
    self.camera.brightness = 30
    self.camera.contrast = 90
    self.camera.exposure_mode = 'verylong'
    self.camera.meter_mode = 'spot'
    self.camera.shutter_speed = 25000
    self.camera.color_effects = (128, 128)

  def __enter__(self):
    self.setup()
    return self

  def __exit__(self, type, value, traceback):
    self.cleanup()

  def setup(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in self.led_pins:
      GPIO.setup(pin, GPIO.OUT)

  def set_leds(self, value):
    for pin in self.led_pins:
      GPIO.output(pin, value)

  def leds_on(self):
    self.set_leds(GPIO.HIGH)

  def leds_off(self):
    self.set_leds(GPIO.LOW)

  def capture(self, out):
    self.leds_on()
    self.camera.capture(out, 'jpeg')
    self.leds_off()

  def cleanup(self):
    self.leds_off()
    GPIO.cleanup()
