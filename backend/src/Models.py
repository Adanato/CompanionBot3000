from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from Models import GPTModel
from LLM import SupportChat
from TTS import TextToSpeech

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the models
chat = SupportChat(GPTModel(model="gpt-4o"))
textConverter = TextToSpeech()

@socketio.on('start_recording')
def handle_start_recording():
    """
    Notify server to prepare for new recording session.
    """
    print("Recording started")

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_data):
    """
    Handle received audio chunks from client.
    This example assumes incoming audio chunks are processed later.
    """
    # Currently, we are focusing on returning text/audio back, so we'll skip STT processing.
    print("Received audio chunk")

@socketio.on('audio_stop')
def handle_audio_stop():
    """
    Process input text and send back both text and audio.
    """
    # Simulate user input for demo purposes (replace with actual transcription in production)
    user_text = "This is a sample user input text."

    # Generate chat response
    support_text = chat.generate(prompt=user_text)

    # Emit text response
    emit('text_response', {"text": support_text})

    # Stream audio response
    for audio_chunk in textConverter.streamSpeech(support_text):
        emit('audio_stream', audio_chunk)

    # Notify the client that streaming is complete
    emit('audio_complete')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
