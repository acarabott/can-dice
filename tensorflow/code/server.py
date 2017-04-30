from flask import Flask
from flask import request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './server-data'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello():
  return "Hello World!"


@app.route('/classify', methods=['GET', 'POST'])
def classify():
  print('classify')
  print(request.method)
  if request.method == 'POST':
    if 'img' not in request.files:
      return 'you need to POST an image with key img'
    file = request.files['img']

    if file.filename == '':
      return 'empty file posted'

    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return 'File uploaded!'

  else:
    return 'whatcha wanna classify?'


if __name__ == '__main__':
  app.run(debug=True)
