from collections import defaultdict
import numpy as np
import json
from TextAnalyzer import TextAnalyzer
import nltk
nltk.download('vader_lexicon')

class MentalHealthModel():
    def __init__(self, chat_model, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.chat_model = chat_model
        self.text_analyzer = TextAnalyzer()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        self.response_templates = {
            'empathetic': "I understand you're feeling {emotion}. {response}",
            'solution_focused': "Let's work on addressing your {issue}. {response}",
            'reflective': "It sounds like {situation}. {response}",
            'directive': "I recommend {action} to help with your {issue}. {response}"
        }
    
    def calculate_state_value(self, features):
        """Calculate a numerical value representing emotional state"""
        # Combine sentiment and emotion scores into a single value
        sentiment_score = features['sentiment']['vader']['compound']
        
        # Get positive emotions (joy, love) vs negative emotions (sadness, anger, fear)
        emotion_scores = features['emotion']
        positive_emotions = emotion_scores.get('joy', 0) + emotion_scores.get('love', 0)
        negative_emotions = (emotion_scores.get('sadness', 0) + 
                           emotion_scores.get('anger', 0) + 
                           emotion_scores.get('fear', 0))
        
        # Combine into single state value (-1 to 1 scale)
        emotion_balance = positive_emotions - negative_emotions
        state_value = (sentiment_score + emotion_balance) / 2
        
        return state_value
    
    def calculate_reward(self, initial_state_value, next_state_value):
        """Calculate reward based on improvement in emotional state"""
        # Reward is based on the change in emotional state
        base_reward = next_state_value - initial_state_value
        
        # Scale reward to emphasize improvements
        if base_reward > 0:
            reward = 2 * base_reward  # Amplify positive changes
        else:
            reward = base_reward      # Keep negative changes as is
            
        # Add small positive reward for maintaining good states
        if next_state_value > 0.5 and initial_state_value > 0.5:
            reward += 0.1
            
        return reward
    
    def _get_state_key(self, features):
        """Convert features to a state key for Q-table"""
        sentiment = features['sentiment']['vader']['compound']
        dominant_emotion = max(features['emotion'].items(), key=lambda x: x[1])[0]
        word_count_bucket = min(features['word_count']['total_words'] // 10, 5)
        
        # Include emotion intensities in state
        emotion_intensities = '_'.join(
            f"{k[:2]}{v:.1f}" 
            for k, v in sorted(features['emotion'].items())
            if v > 0.2  # Only include significant emotions
        )
        
        return f"s_{sentiment:.1f}_{dominant_emotion}_{word_count_bucket}_{emotion_intensities}"
    
    def _get_best_action(self, state):
        """Choose best action based on Q-values with epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.choice(list(self.response_templates.keys()))
        
        q_values = self.q_table[state]
        if not q_values:
            return np.random.choice(list(self.response_templates.keys()))
            
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def generate(self, user_text, conversation_history=None):
        """Generate response using current policy"""
        features = self.text_analyzer.extract_features(user_text)
        if conversation_history:
            long_term_features = self.text_analyzer.extract_long_term_features(conversation_history)
            features.update(long_term_features)
            
        state = self._get_state_key(features)
        state_value = self.calculate_state_value(features)
        action = self._get_best_action(state)
        
        prompt = f"""User Message: {user_text}
        Features: {json.dumps(features, indent=2)}
        Response Style: {action}
        
        Generate a response that is:
        1. Aligned with the detected emotional state
        2. Appropriate for the sentiment level
        3. Following the {action} template
        4. Aimed at improving the user's emotional state
        """
        
        base_response = self.chat_model.generate(prompt)
        
        return {
            'response': self.response_templates[action].format(
                emotion=max(features['emotion'].items(), key=lambda x: x[1])[0],
                issue='concern',
                situation=user_text[:50] + "..." if len(user_text) > 50 else user_text,
                action='taking deep breaths',
                response=base_response
            ),
            'state': state,
            'state_value': state_value,
            'action': action,
            'features': features
        }
    
    def update(self, initial_state, action, next_state_value, initial_state_value):
        """Update Q-values based on state improvement"""
        reward = self.calculate_reward(initial_state_value, next_state_value)
        
        # Get best Q-value for next state
        next_best_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0
        
        # Q-learning update rule
        current_q = self.q_table[initial_state][action]
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_best_q - current_q
        )
        self.q_table[initial_state][action] = new_q
        
        return reward
    
    def save_model(self, filepath):
        """Save Q-table to file"""
        with open(filepath, 'w') as f:
            json.dump(dict(self.q_table), f)
    
    def load_model(self, filepath):
        """Load Q-table from file"""
        with open(filepath, 'r') as f:
            self.q_table = defaultdict(lambda: defaultdict(float), json.load(f))