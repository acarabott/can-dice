from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import g
from flask.json import dumps

from flask_sockets import Sockets
import gevent.wsgi
from geventwebsocket.handler import WebSocketHandler
import werkzeug.serving

import atexit
import datetime
import time
import io
import os
import sqlite3

from Brain import Brain
import dice_processing


UPLOAD_FOLDER = 'uploads'
UPLOAD_LIMIT = 10
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
MODEL_PATH = 'model.pb'
LABELS_PATH = 'labels.txt'
DATABASE = 'dice.db'
IMAGE_ROUTE = '/image/'

brain = Brain(MODEL_PATH, LABELS_PATH)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_LIMIT'] = UPLOAD_LIMIT
app.config['DATABASE'] = DATABASE

sockets = Sockets(app)

clients = []

# Database bizniz --------------------------------------------------------------


def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(app.config['DATABASE'],
                                       detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  db.row_factory = sqlite3.Row
  return db


@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()


def query_db(query, args=(), one=False):
  cur = get_db().execute(query, args)
  rv = cur.fetchall()
  return (rv[0] if rv else None) if one else rv


def db_insert_result(filename, result):
  print(filename, result)
  db = get_db()
  cursor = db.cursor()
  now = datetime.datetime.now()
  cursor.execute('INSERT INTO dice VALUES (?,?,?)', (filename, result, now))
  db.commit()


def create_db():
  with app.app_context():
    with open(DATABASE, 'wb') as db:
      db = get_db()
      db.execute('CREATE TABLE dice (filename text, result int, ts timestamp)')
      db.commit()
      db.close()


def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()


def get_results():
  rows = query_db('select * from dice')
  results = [{'src': '{}{}'.format(IMAGE_ROUTE, r[0]), 'result': r[1]} for r in rows]
  return results


# Sockets ----------------------------------------------------------------------


@sockets.route('/connect')
def connect_socket(ws):
  clients.append(ws)

  while not ws.closed:
    ws.receive()

  clients.remove(ws)


def notify_clients():
  results = get_results()
  json = dumps(results)
  for client in clients:
    client.send(json)

# Image handling ---------------------------------------------------------------


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
  date_str = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')
  filename = os.path.join(app.config['UPLOAD_FOLDER'], '{}.jpg'.format(date_str))
  file.save(filename)
  return filename


def classify_image(file):
  cropped = dice_processing.crop_dice(file)
  results = []

  for img in cropped:
    with io.BytesIO() as output:
       img.convert('RGB').save(output, 'JPEG')
       data = output.getvalue()
       result = brain.classify(data)
       results.append(str(result[0]))

  result = int(''.join(str(i) for i in results))
  return result


def clean_uploads():
  uploads = os.listdir(app.config['UPLOAD_FOLDER'])
  oldest = uploads[::-1][app.config['UPLOAD_LIMIT']:]

  for ul in oldest:
    ul_full = os.path.join(app.config['UPLOAD_FOLDER'], ul)
    try:
      os.remove(ul_full)
    except OSError as e:
      print("couldn't delete file {}".format(ul_full))
      pass


def cleanup():
  global brain
  brain.exit()


# Primary Routing --------------------------------------------------------------

@app.route('/')
def index():
  return render_template('index.html', results=get_results())


@app.route('{}<path:filename>'.format(IMAGE_ROUTE))
def get_image(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'],
                             filename,
                             as_attachment=True)


@app.route('/classify', methods=['GET', 'POST'])
def classify():
  if request.method == 'POST':
    if 'img' not in request.files:
      return 'you need to POST an image with key img'

    file = request.files['img']

    if file.filename == '':
      return 'empty file posted'

    if file and allowed_file(file.filename):
      saved_path = save_image(file)
      clean_uploads()
      result = classify_image(file)
      db_insert_result(os.path.basename(saved_path), result)
      notify_clients()

      print('{} - {}'.format(result, time.asctime()))
      return str(result)

  else:
    return "you need to POST a jpg to this url with file key 'img'"


@werkzeug.serving.run_with_reloader
def run_server():
  app.debug = True
  server = gevent.wsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
  server.serve_forever()


if __name__ == '__main__':
  atexit.register(cleanup)
  os.makedirs(UPLOAD_FOLDER, mode=0o755, exist_ok=True)
  run_server()
