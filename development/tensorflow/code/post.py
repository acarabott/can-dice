import requests
import os

url = 'http://localhost:5000/classify'

data_set = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05b-labelled/'

imgs = [os.path.join(data_set, i) for i in ['6/15251.jpg', '4/00070.jpg', '1/00123.jpg']]

for img in imgs:
  files = {'img': open(img, 'rb')}
  r = requests.post(url, files=files)
  print(r.text)
