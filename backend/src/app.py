from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from Models import GPTModel

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
chat = GPTModel(model="gpt-4o")

def send_wav_file(filepath):
    """Helper function to read and send WAV file"""
    try:
        with open(filepath, 'rb') as audio_file:
            audio_data = audio_file.read()
            emit('audio_response', audio_data)
    except Exception as e:
        print(f"Error reading audio file: {e}")
        emit('error', {"error": "Failed to load audio file"})

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('connection_status', {"message": "Connected"})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('send_text')
def handle_text(data):
    try:
        user_text = data.get("text", "")
        if not user_text:
            emit('error', {"error": "No text provided"})
            return

        print(f"Received text: {user_text}")
        support_text = chat.generate(prompt=user_text)
        emit('text_response', {"text": support_text})
        
        # Send audio file response
        wav_filepath = "Chorus.wav"  # TEST
        send_wav_file(wav_filepath)
        
    except Exception as e:
        print(f"Error in handle_text: {e}")
        emit('error', {"error": str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)