
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base, Tag, Vehiculo, Posicion, Configuracion
from datetime import datetime

app = Flask(__name__)
DATABASE_URL = 'sqlite:///uwb_tracking.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Gestión UWB</title>
    <style>
        table { border-collapse: collapse; width: 100%%; margin-bottom: 30px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #eee; }
        form { margin-bottom: 40px; }
        input[type=text], input[type=number] { width: 200px; padding: 5px; margin: 5px; }
        input[type=submit] { padding: 5px 15px; }
    </style>
</head>
<body>
    <h1>Gestión del sistema UWB</h1>

    <h2>Registrar nuevo Tag y Configuración</h2>
    <form method="POST" action="/add_tag">
        <label>Tag ID:</label><input type="text" name="tag_id" required><br>
        <label>Sleep Interval (ms):</label><input type="number" name="sleep_interval_ms" required><br>
        <label>Transmit Offset (ms):</label><input type="number" name="transmit_offset_ms" required><br>
        <label>Canal:</label><input type="number" name="channel" required><br>
        <input type="submit" value="Registrar">
    </form>

    <h2>Modificar Configuración de Tag</h2>
    <form method="POST" action="/update_config">
        <label>Tag ID:</label><input type="text" name="tag_id" required><br>
        <label>Sleep Interval (ms):</label><input type="number" name="sleep_interval_ms"><br>
        <label>Transmit Offset (ms):</label><input type="number" name="transmit_offset_ms"><br>
        <label>Canal:</label><input type="number" name="channel"><br>
        <input type="submit" value="Actualizar">
    </form>

    <h2>Tags</h2>
    <table>
        <tr><th>ID</th><th>Última conexión</th></tr>
        {% for tag in tags %}
        <tr><td>{{ tag.id }}</td><td>{{ tag.last_seen }}</td></tr>
        {% endfor %}
    </table>

    <h2>Configuraciones</h2>
    <table>
        <tr><th>Tag ID</th><th>Sleep Interval (ms)</th><th>Offset (ms)</th><th>Canal</th></tr>
        {% for c in configuraciones %}
        <tr><td>{{ c.tag_id }}</td><td>{{ c.sleep_interval_ms }}</td><td>{{ c.transmit_offset_ms }}</td><td>{{ c.channel }}</td></tr>
        {% endfor %}
    </table>

    <h2>Últimas Posiciones</h2>
    <table>
        <tr><th>Tag ID</th><th>X</th><th>Y</th><th>Timestamp</th></tr>
        {% for p in posiciones %}
        <tr><td>{{ p.tag_id }}</td><td>{{ p.x }}</td><td>{{ p.y }}</td><td>{{ p.timestamp }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
'''

@app.route('/')
def index():
    session = Session()
    tags = session.query(Tag).all()
    configuraciones = session.query(Configuracion).all()
    posiciones = session.query(Posicion).order_by(Posicion.timestamp.desc()).limit(10).all()
    session.close()
    return render_template_string(TEMPLATE, tags=tags, configuraciones=configuraciones, posiciones=posiciones)

@app.route('/add_tag', methods=['POST'])
def add_tag():
    tag_id = request.form['tag_id']
    sleep = int(request.form['sleep_interval_ms'])
    offset = int(request.form['transmit_offset_ms'])
    channel = int(request.form['channel'])

    session = Session()
    if not session.query(Tag).filter_by(id=tag_id).first():
        session.add(Tag(id=tag_id, last_seen=datetime.utcnow()))
    session.merge(Configuracion(tag_id=tag_id, sleep_interval_ms=sleep, transmit_offset_ms=offset, channel=channel))
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/update_config', methods=['POST'])
def update_config():
    tag_id = request.form['tag_id']
    sleep = request.form.get('sleep_interval_ms')
    offset = request.form.get('transmit_offset_ms')
    channel = request.form.get('channel')

    session = Session()
    config = session.query(Configuracion).filter_by(tag_id=tag_id).first()
    if config:
        if sleep: config.sleep_interval_ms = int(sleep)
        if offset: config.transmit_offset_ms = int(offset)
        if channel: config.channel = int(channel)
        session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/get_config')
def get_config():
    tag_id = request.args.get('tag_id')
    if not tag_id:
        return jsonify({'error': 'Missing tag_id'}), 400

    session = Session()
    config = session.query(Configuracion).filter_by(tag_id=tag_id).first()
    session.close()

    if config:
        return jsonify({
            'sleep_interval_ms': config.sleep_interval_ms,
            'transmit_offset_ms': config.transmit_offset_ms,
            'channel': config.channel
        })
    else:
        return jsonify({'error': 'Configuration not found for tag_id'}), 404

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.get_json()
    tag_id = data.get('tag_id')
    x = data.get('x')
    y = data.get('y')

    if not tag_id or x is None or y is None:
        return jsonify({'error': 'Missing tag_id, x, or y'}), 400

    session = Session()

    tag = session.query(Tag).filter_by(id=tag_id).first()
    if not tag:
        tag = Tag(id=tag_id, last_seen=datetime.utcnow())
        session.add(tag)
    else:
        tag.last_seen = datetime.utcnow()

    nueva_pos = Posicion(tag_id=tag_id, x=x, y=y)
    session.add(nueva_pos)

    session.commit()
    session.close()

    return jsonify({'status': 'position updated'})

if __name__ == '__main__':
    app.run(port=5000)
