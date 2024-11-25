from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

# Flask application and SocketIO setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Không cần `engineio_logger` hoặc `socketio_logger` trừ khi bạn cần ghi log chi tiết
socketio = SocketIO(app, cors_allowed_origins="*")  # Không dùng `async_mode='threading'`

# Route for root URL
@app.route('/')
def index():
    return "<h1>Hello world</h1>"

# Route to handle POST request and send data to all sockets
@app.route('/sendData', methods=['POST'])
def send_data():
    # Gửi dữ liệu qua WebSocket
    socketio.emit('event', {'message': 'Hello from server!'})
    return jsonify({})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print("User connected!")
    emit('event', {'message': 'Connected !!!!'})

@socketio.on('status')
def handle_status(data):
    print(f"Status received from client: {data}")

# Run the server
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
