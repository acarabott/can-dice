from flask import Flask
from flask import request
from Brain import Brain
import atexit
import tempfile

UPLOAD_FOLDER = './server-data'
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
      with tempfile.NamedTemporaryFile(suffix='.jpg', prefix='dice') as tmp:
        file_path = tmp.name
        file.save(file_path)
        result = brain.run(file_path)
        return str(result[0])

  else:
    return "you need to POST a jpg to this url with file key 'img'"


def cleanup():
  global brain
  brain.exit()


if __name__ == '__main__':
  atexit.register(cleanup)
  app.run(host='0.0.0.0', debug=True)
