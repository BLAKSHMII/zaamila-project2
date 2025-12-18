from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print("Client connected")
    emit('server_message', {'data': 'Connected to Flask WebSocket Server'})

@socketio.on('disconnect')
def on_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True)
