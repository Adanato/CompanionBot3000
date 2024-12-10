import torch
from melo.api import TTS
import nltk
nltk.download('averaged_perceptron_tagger_eng')

class TextToSpeech:
    def __init__(self):
        # Get device
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # Init TTS
        self.model = TTS(language='EN', device=device)

    def convertToSpeech(self, text):
        speaker_ids = self.model.hps.data.spk2id
        # American accent
        output_path = './temp/out.wav'
        self.model.tts_to_file(text, speaker_ids['EN-BR'], output_path, speed=1)
        return output_path