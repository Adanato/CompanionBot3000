import torch
from TTS.api import TTS

class TextToSpeech:
    def __init__(self, model="tts_models/multilingual/multi-dataset/xtts_v2"):
        # Get device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Init TTS
        self.tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False).to(device)

    def convertToSpeech(self, text):
        #returns audio or file location
        return self.tts.tts(text=text, speaker_wav="my/cloning/audio.wav", language="en")
