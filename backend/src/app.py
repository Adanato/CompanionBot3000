from flask import Flask, request, Response
from flask_cors import CORS
from Models import GPTModel
from LLM import SupportChat
from TTS import TextToSpeech

app = Flask(__name__)
CORS(app)

# Initialize the models
chat = SupportChat(GPTModel(model="gpt-4o"))
textConverter = TextToSpeech()

@app.route('/text_and_audio_stream', methods=['POST'])
def text_and_audio_stream():
    """
    Endpoint to return text in the initial part of the response and stream audio as a multipart response.
    """
    try:
        # Extract user text from request JSON
        user_text = request.json.get('text', '')
        if not user_text:
            return {"error": "No text provided"}, 400

        # Generate chat response
        support_text = chat.generate(prompt=user_text)

        # Create generator for streaming audio and text
        def generate_response():
            # Yield the text response as part of the stream
            yield f"--boundary\r\nContent-Type: application/json\r\n\r\n"
            yield f'{{"text": "{support_text}"}}\r\n'
            
            # Yield the audio as a binary stream
            yield f"--boundary\r\nContent-Type: audio/mpeg\r\n\r\n"
            for audio_chunk in textConverter.streamSpeech(support_text):
                yield audio_chunk
            yield f"--boundary--\r\n"

        return Response(
            generate_response(),
            mimetype="multipart/x-mixed-replace; boundary=boundary"
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
