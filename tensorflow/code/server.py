from flask import Flask
from flask import request
import classify_image as brain
import atexit
import tempfile

UPLOAD_FOLDER = './server-data'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
MODEL_DIR = '/Users/ac/rca-dev/17-02-change-a-number/can-dice/tensorflow/trained-models/98.4-dice-i05b-labelled-s50000-r0.01-a98.4'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello():
  return "Hello World!"


@app.route('/classify', methods=['GET', 'POST'])
def classify():
  if request.method == 'POST':
    if 'img' not in request.files:
      return 'you need to POST an image with key img'
    file = request.files['img']

    if file.filename == '':
      return 'empty file posted'

    if file and allowed_file(file.filename):
      with tempfile.NamedTemporaryFile(suffix='.jpg', prefix='dice') as tmp:
        file_path = tmp.name
        file.save(file_path)
        result = brain.run(file_path)
        return 'result: {}'.format(result)

  else:
    return 'you need to POST to this url'


def setup():
  brain.setup(MODEL_DIR)


def cleanup():
  brain.cleanup()


if __name__ == '__main__':
  setup()
  atexit.register(cleanup)
  app.run(debug=True)
