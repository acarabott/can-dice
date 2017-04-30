import requests

url = 'http://localhost:5000/classify'

img = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/data-set/05b-labelled/6/15251.jpg'

files = {'img': open(img, 'rb')}
r = requests.post(url, files=files)

print(r.text)
