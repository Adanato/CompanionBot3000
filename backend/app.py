from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from io import BytesIO

# Custom classes

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Buffer to store audio chunks
audio_buffer = BytesIO()

#start async model
vllm = asyncVLLM(model="LLama3.1")


@socketio.on('audio_chunk')
def handle_audio_chunk(audio_data):
    # Store audio chunks in the buffer
    audio_buffer.write(audio_data)

@socketio.on('audio_stop')
def handle_audio_stop():
    # Reset the buffer's pointer to the beginning
    audio_buffer.seek(0)

    

    TTS = TTS()
    audio = TTS.convertToSpeech()
    # Emit the full audio back to the client
    emit('playAudio', audio_buffer.read(), broadcast=True)

    # Clear the buffer for the next recording session
    audio_buffer.truncate(0)
    audio_buffer.seek(0)

@socketio.on('start_recording')
def handle_start_recording():
    # Clear the buffer when a new recording starts
    audio_buffer.truncate(0)
    audio_buffer.seek(0)

    #process the audio to text
    STT = STT()
    text = STT.convertToText(audio)
    # send text through RL
    text = RL.adapt(text)
    # send text to asyncVLLM
        vllm.generate(prompt=text)
    
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
