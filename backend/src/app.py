from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from Models import GPTModel
from LLM import SupportChat
from TTS import TextToSpeech

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize models
chat = SupportChat(GPTModel(model="gpt-4o"))
textConverter = TextToSpeech()

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection.
    """
    print("Client connected")
    emit('connection_status', {"message": "Connection established"})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    print("Client disconnected")

@socketio.on('send_text')
def handle_text(data):
    """
    Handle incoming text and send back both text and audio.
    """
    # Extract user text
    user_text = data.get("text", "")
    if not user_text:
        emit('error', {"error": "No text provided"})
        return

    print(f"Received text: {user_text}")

    # Generate response using chat model
    support_text = chat.generate(prompt=user_text)

    # Emit the generated text response
    emit('text_response', {"text": support_text})

    # Stream the generated audio response
    for audio_chunk in textConverter.streamSpeech(support_text):
        emit('audio_stream', audio_chunk)

    # Notify client that audio streaming is complete
    emit('audio_complete')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
