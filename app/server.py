import os
import argparse
from sys import argv
import time
from pathlib import Path
from threading import Thread, Event

from flask import Flask, render_template, request, abort, send_from_directory
from flask_socketio import SocketIO, emit


# -------- CONFIGURACIÓN INICIAL --------
parser = argparse.ArgumentParser(description='SideEdit')
parser.add_argument('--host', default='127.0.0.1', help='Host a usar (default: 127.0.0.1)')
parser.add_argument('--port', type=int, default=5005, help='Puerto a usar (default: 5005)')
parser.add_argument('--folder_watch', default='../editable', help='Carpeta de archivos JS (default: ../editable)')

args = parser.parse_args()

HOST = args.host
PORT = args.port
LIVE_DIR = Path(__file__).parent / args.folder_watch
LIVE_DIR.mkdir(exist_ok=True)


# -------- FLASK APP --------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'K-sideedit-E-0987654321-Y'
socketio = SocketIO(app, cors_allowed_origins="*")


# -------- ESTADO GLOBAL --------
watched_file = None
stop_event = Event()
watch_thread = None
TEXTO_INICIAL = '// Editar y guardar para recarga automática\n'
DEBUG = False


# -------- UTILIDADES --------
def sanitize_filename(filename: str) -> str:
    if not filename.endswith('.js'):
        raise ValueError("Solo se permiten archivos .js")
    name = os.path.basename(filename)
    if name != filename:
        raise ValueError("Ruta inválida: solo nombres de archivo, sin directorios")
    if '..' in name or name.startswith('.'):
        raise ValueError("Nombre de archivo no permitido")
    return name

def watch_file(filepath: Path):
    last_modified = filepath.stat().st_mtime
    while not stop_event.is_set():
        try:
            current_modified = filepath.stat().st_mtime
            if current_modified != last_modified:
                last_modified = current_modified
                socketio.emit('file_changed', namespace='/watch')
            time.sleep(0.3)
        except (OSError, FileNotFoundError):
            socketio.emit('file_error', {'message': 'Archivo ya no accesible'}, namespace='/watch')
            break


# -------- SOCKETS --------
@socketio.on('set_watch_file', namespace='/watch')
def handle_set_watch_file(data):
    global watched_file, watch_thread, stop_event
    raw_name = data.get('filename', '').strip()
    try:
        safe_name = sanitize_filename(raw_name)
        filepath = LIVE_DIR / safe_name
        if not filepath.exists():
            filepath.write_text(TEXTO_INICIAL, encoding='utf-8')
        if watch_thread and watch_thread.is_alive():
            stop_event.set()
            watch_thread.join(timeout=1)
        stop_event.clear()
        watched_file = filepath
        watch_thread = Thread(target=watch_file, args=(filepath,), daemon=True)
        watch_thread.start()
        emit('watch_started', {'filename': safe_name}, namespace='/watch')
    except Exception as e:
        emit('file_error', {'message': str(e)}, namespace='/watch')


# -------- RUTAS --------
@app.route('/read_js')
def read_js():
    filename = request.args.get('name', '')
    try:
        safe_name = sanitize_filename(filename)
        filepath = LIVE_DIR / safe_name
        if not filepath.exists():
            abort(404)
        return send_from_directory(LIVE_DIR, safe_name, mimetype='application/javascript')
    except Exception:
        abort(403)

@app.route('/sideedit.js')
def sideeditjs():
    try:
        socket_io_path = Path(__file__).parent / 'static' / 'socket.io.min.js'
        sideedit_path = Path(__file__).parent / 'static' / 'sideedit.js'

        if not socket_io_path.exists():
            return "Error: static/socket.io.min.js no encontrado", 500
        if not sideedit_path.exists():
            return "Error: static/sideedit.js no encontrado", 500

        with open(socket_io_path, 'r', encoding='utf-8') as f:
            code_socket_io = f.read()
        with open(sideedit_path, 'r', encoding='utf-8') as f:
            code_sideedit = f.read()

        code_url = f"const server_local = 'http://{HOST}:{PORT}';"
        content = f'{code_socket_io}\n\n{code_url}\n\n{code_sideedit}'
        return content, {'Content-Type': 'application/javascript; charset=utf-8'}
    except Exception as e:
        return f"Error al cargar sideedit.js: {str(e)}", 500

@app.route('/')
def index():
    return render_template('index.html', host=HOST, port=PORT)


# -------- EJECUCIÓN --------
if __name__ == '__main__':
    print(f"Carpeta de trabajo: {LIVE_DIR.resolve()}")
    print(f"Servidor iniciado en: http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
