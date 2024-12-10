from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os

class GPTModel():
    def __init__(self, model="gpt-4o"):
        self.model_id = model
        self.conversation_history = []
        
    def generate(self, prompt):
        client = OpenAI()
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": prompt})
        
        # Prepare messages with full conversation history
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages.extend(self.conversation_history)
        
        completion = client.chat.completions.create(
            model=self.model_id,
            messages=messages
        )
        
        # Store assistant's response in history
        assistant_message = completion.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
        
    def clear_history(self):
        self.conversation_history = []