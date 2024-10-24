from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

# Create a Flask application
app = Flask(__name__)

# Initialize Flask-SocketIO
socketio = SocketIO(app)

# Define a route for the homepage
@app.route('/')
def index():
    return render_template('index.html')  # Serve an HTML page (optional)

# Event handler for when a client connects
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('message', 'Welcome to the WebSocket!')

# Event handler for when a client sends a message
@socketio.on('message')
def handle_message(message):
    print(f"Received message: {message}")
    send(message, broadcast=True)  # Broadcast the message to all clients

# Event handler for when a client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

# Run the Flask app with WebSocket support
if __name__ == '__main__':
    # Use eventlet or gevent as the async mode
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
