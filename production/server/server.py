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
import io
import os
import sqlite3

from Brain import Brain
import dice_processing

DEBUG = True
DEBUG_FOLDER = 'debug'
UPLOAD_FOLDER = 'uploads'
HISTORY_LIMIT = 10
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
MODEL_PATH = 'model.pb'
LABELS_PATH = 'labels.txt'
DATABASE = 'dice.db'
IMAGE_ROUTE = '/image/'

brain = Brain(MODEL_PATH, LABELS_PATH)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUG_FOLDER'] = DEBUG_FOLDER
app.config['HISTORY_LIMIT'] = HISTORY_LIMIT
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
  db = get_db()
  cur = db.execute(query, args)
  rv = cur.fetchall()
  db.commit()
  return (rv[0] if rv else None) if one else rv


def db_insert_result(filename, value):
  now = datetime.datetime.now()
  query_db('INSERT INTO dice VALUES (?,?,?)', (filename, value, now))


def create_db():
  with app.app_context():
    with open(DATABASE, 'wb') as db:
      db = get_db()
      db.execute('CREATE TABLE dice (filename text, value text, ts timestamp)')
      db.commit()
      db.close()


def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()


def get_results():
  rows = query_db('select * from dice ORDER BY ts DESC')
  results = [{'src': '{}{}'.format(IMAGE_ROUTE, r[0]),
              'value': r[1],
              'time': r[2]} for r in rows]
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
  values = []

  for i, img in enumerate(cropped):
    with io.BytesIO() as output:
       img.convert('RGB').save(output, 'JPEG')
       if DEBUG:
         debug_path = os.path.join(app.config['DEBUG_FOLDER'], '{}.jpg'.format(i))
         img.save(debug_path, 'JPEG')

       data = output.getvalue()

       value = brain.classify(data)
       values.append(str(value[0]))

  value = ''.join(str(i) for i in values)
  return value


def remove_old():
  count = query_db('SELECT COUNT(*) FROM dice')[0][0]
  remove_count = max(0, count - app.config['HISTORY_LIMIT'])
  to_remove = query_db('SELECT rowid, filename FROM dice ORDER by ts ASC LIMIT (?)', (remove_count,))

  # delete from database
  delete_sql = 'DELETE FROM dice WHERE rowid IN ({})'.format(','.join('?' * remove_count))
  remove_ids = [r[0] for r in to_remove]
  query_db(delete_sql, remove_ids)

  # delete image files
  remove_filenames = [r[1] for r in to_remove]

  for filename in remove_filenames:
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
      os.remove(path)
    except FileNotFoundError as e:
      print("file not found, couldn't delete")
    except OSError as e:
      print("couldn't delete file {}".format(path))


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
      value = classify_image(file)
      db_insert_result(os.path.basename(saved_path), value)
      remove_old()
      notify_clients()

      return str(value)

  else:
    return "you need to POST a jpg to this url with file key 'img'"


@werkzeug.serving.run_with_reloader
def run_server():
  # app.debug = True
  server = gevent.wsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
  server.serve_forever()


if __name__ == '__main__':
  atexit.register(cleanup)
  os.makedirs(UPLOAD_FOLDER, mode=0o755, exist_ok=True)
  run_server()
