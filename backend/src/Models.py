from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os

class GPTModel():
    def __init__(self, model="gpt-4o"):
        self.model_id = model
    def generate(self, prompt):
        client = OpenAI()

        completion = client.chat.completions.create(
        model=self.model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        )


        return completion.choices[0].message.content
    


