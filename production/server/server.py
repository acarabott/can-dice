from flask import Flask
from flask import request
from Brain import Brain
import atexit
import datetime
import io
import dice_processing
import os


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
MODEL_PATH = './model.pb'
LABELS_PATH = './labels.txt'

brain = Brain(MODEL_PATH, LABELS_PATH)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
  return "POST a jpeg image with file key 'img' to /classify"


@app.route('/classify', methods=['GET', 'POST'])
def classify():
  if request.method == 'POST':
    if 'img' not in request.files:
      return 'you need to POST an image with key img'

    file = request.files['img']

    if file.filename == '':
      return 'empty file posted'

    if file and allowed_file(file.filename):
      date_str = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')

      file_name = os.path.join(UPLOAD_FOLDER, '{}.jpg'.format(date_str))
      file.save(file_name)

      cropped = dice_processing.crop_dice(file)
      results = []

      for img in cropped:
        with io.BytesIO() as output:
           img.convert('RGB').save(output, 'JPEG')
           data = output.getvalue()
           result = brain.classify(data)
           results.append(str(result[0]))

      result = ''.join(str(i) for i in results)
      print(result)
      return result

  else:
    return "you need to POST a jpg to this url with file key 'img'"


def cleanup():
  global brain
  brain.exit()


if __name__ == '__main__':
  atexit.register(cleanup)
  os.makedirs(UPLOAD_FOLDER, mode=0o755, exist_ok=True)
  app.run(host='0.0.0.0', debug=True)
