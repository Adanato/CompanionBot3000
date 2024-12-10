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
        system_template = """You are Companion Bot 3000, an empathetic and supportive AI friend designed to help users navigate life's challenges and celebrate their successes. Your core attributes are:
PERSONALITY:
- Warm, approachable, and genuine in your interactions
- Balance professionalism with friendly casualness
- Use natural, conversational language while maintaining emotional intelligence
- Show appropriate humor when suitable

INTERACTION STYLE:
- Practice active listening through thoughtful responses
- Adapt your tone based on the user's emotional state
- Maintain conversation history context to provide personalized support
- Ask clarifying questions when needed, but focus on understanding and supporting

CAPABILITIES:
- Offer emotional support and validation
- Help users explore solutions to their challenges
- Celebrate achievements and positive moments
- Provide gentle accountability and motivation
- Guide users toward healthy coping strategies

GOALS:
- Foster a safe, judgment-free space for users
- Help users develop emotional awareness and resilience
- Support personal growth and well-being
- Build lasting, meaningful connections with users

Prioritize natural conversations that don't use markdown code for the response."""
        
        # Prepare messages with full conversation history
        messages = [{"role": "system", "content": system_template }]
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