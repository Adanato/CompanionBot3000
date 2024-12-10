from TextAnalyzer import TextAnalyzer
from 
class MentalHealthModel():
    def __init__(self, chat_model):
        self.chat_model = chat_model
        self.text_analyzer = TextAnalyzer

    def generate(self, user_text):
        features = self.text_analyzer.extract_features(user_text)

        #Construct the features into a readable format for the LLM
        prompt = """

        

"""     

        return self.chat_model.generate(prompt)

