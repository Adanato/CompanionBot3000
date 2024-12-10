from collections import defaultdict
import numpy as np
import json
from TextAnalyzer import TextAnalyzer
import logging

class MentalHealthModel:
    def __init__(self, chat_model, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self._setup_logging()
        self._initialize_components(chat_model, learning_rate, discount_factor, epsilon)
        self._load_response_templates()
        
    def _setup_logging(self):
        """Initialize logging configuration"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _initialize_components(self, chat_model, learning_rate, discount_factor, epsilon):
        """Initialize model components and parameters"""
        self.chat_model = chat_model
        self.text_analyzer = self._create_text_analyzer()
        
        # Model parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # State tracking
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.previous_state = None
        self.previous_action = None
        self.previous_state_value = None
        self.conversation_history = []
        
    def _create_text_analyzer(self):
        """Create text analyzer with error handling"""
        try:
            return TextAnalyzer()
        except Exception as e:
            self.logger.error(f"Failed to initialize TextAnalyzer: {e}")
            raise

    def _load_response_templates(self):
        """Load response templates for different conversation styles"""
        self.response_templates = {
            'empathetic': {
                'template': "I understand you're feeling {emotion}. {response}",
                'guidance': "Show understanding and validation of the user's emotions."
            },
            'solution_focused': {
                'template': "Let's work on addressing your {issue}. {response}",
                'guidance': "Offer practical steps and actionable solutions."
            },
            'reflective': {
                'template': "It sounds like {situation}. {response}",
                'guidance': "Mirror the user's feelings and experiences."
            },
            'directive': {
                'template': "I recommend {action} to help with your {issue}. {response}",
                'guidance': "Provide clear, specific advice while being supportive."
            }
        }

    def process_user_message(self, user_text):
        """Main method to process user messages and generate responses"""
        try:
            features = self._safe_extract_features(user_text)
            current_state = self._create_state_key(features)
            current_state_value = self._calculate_state_value(features)
            
            # Update model if we have previous state
            if self.previous_state:
                self._update_q_values(current_state_value)
            
            # Generate response
            action = self._select_action(current_state)
            response = self._generate_response(user_text, features, action)
            
            # Update tracking
            self._update_history(user_text, response, features, current_state, action)
            self._update_state(current_state, action, current_state_value)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return "I hear you. Could you tell me more about how you're feeling?"

    def _safe_extract_features(self, text):
        """Extract text features with fallback values"""
        try:
            features = self.text_analyzer.extract_features(text)
            return self._validate_features(features, text)
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return self._get_default_features()

    def _validate_features(self, features, text):
        """Ensure all required features are present"""
        if 'emotion' not in features:
            features['emotion'] = {'neutral': 1.0}
        if 'sentiment' not in features:
            features['sentiment'] = {
                'vader': {'compound': 0.0},
                'textblob': {'polarity': 0.0, 'subjectivity': 0.0}
            }
        if 'word_count' not in features:
            features['word_count'] = {
                'total_words': len(text.split()),
                'unique_words': len(set(text.split()))
            }
        return features

    def _get_default_features(self):
        """Provide default features when extraction fails"""
        return {
            'emotion': {'neutral': 1.0},
            'sentiment': {
                'vader': {'compound': 0.0},
                'textblob': {'polarity': 0.0, 'subjectivity': 0.0}
            },
            'word_count': {'total_words': 0, 'unique_words': 0}
        }

    def _create_state_key(self, features):
        """Create a unique state key from features"""
        try:
            sentiment = features.get('sentiment', {}).get('vader', {}).get('compound', 0.0)
            emotions = features.get('emotion', {'neutral': 1.0})
            top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:2]
            emotion_str = '_'.join(f"{e[:3]}{s:.1f}" for e, s in top_emotions)
            
            word_count = features.get('word_count', {}).get('total_words', 0)
            length = 'short' if word_count < 10 else 'medium' if word_count < 30 else 'long'
            
            return f"s_{sentiment:.1f}_{emotion_str}_{length}"
        except Exception as e:
            self.logger.error(f"Error creating state key: {e}")
            return "s_0.0_neutral1.0_short"

    def _select_action(self, state):
        """Select action using epsilon-greedy policy"""
        try:
            if np.random.random() < self.epsilon:
                return np.random.choice(list(self.response_templates.keys()))
            
            q_values = self.q_table[state]
            if not q_values:
                return np.random.choice(list(self.response_templates.keys()))
            
            return max(q_values.items(), key=lambda x: x[1])[0]
        except Exception as e:
            self.logger.error(f"Error selecting action: {e}")
            return 'empathetic'

    def _generate_response(self, user_text, features, action):
        """Generate response using selected action and features"""
        try:
            emotions = features.get('emotion', {'neutral': 1.0})
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            
            prompt = {
                "user_message": user_text,
                "emotional_state": {
                    "dominant_emotion": dominant_emotion,
                    "emotion_intensities": features.get('emotion', {}),
                    "sentiment_scores": features.get('sentiment', {})
                },
                "message_stats": features.get('word_count', {}),
                "conversation_context": self._get_recent_context(),
                "response_parameters": {
                    "style": action,
                    "template": self.response_templates[action]['template'],
                    "guidance": self.response_templates[action]['guidance']
                }
            }
            
            return self.chat_model.generate(json.dumps(prompt, indent=2))
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I hear you. Could you tell me more about how you're feeling?"

    def _get_recent_context(self):
        """Get recent conversation context"""
        try:
            if len(self.conversation_history) >= 2:
                return [
                    {
                        'text': hist['user_text'],
                        'emotions': hist['features'].get('emotion', {}),
                        'sentiment': hist['features'].get('sentiment', {}).get('vader', {}).get('compound', 0.0)
                    }
                    for hist in self.conversation_history[-2:]
                ]
            return None
        except Exception as e:
            self.logger.error(f"Error getting conversation context: {e}")
            return None

    def _calculate_state_value(self, features):
        """Calculate current state value based on features"""
        try:
            sentiment = features.get('sentiment', {}).get('vader', {}).get('compound', 0.0)
            return (sentiment + 1) / 2  # Normalize to [0,1]
        except Exception as e:
            self.logger.error(f"Error calculating state value: {e}")
            return 0.5

    def _update_q_values(self, current_state_value):
        """Update Q-values based on previous state-action pair"""
        try:
            reward = self._calculate_reward(self.previous_state_value, current_state_value)
            
            # Get max Q-value for current state
            next_state = self._create_state_key({
                'sentiment': {'vader': {'compound': current_state_value}},
                'emotion': {'neutral': 1.0},
                'word_count': {'total_words': 0}
            })
            next_q_values = self.q_table[next_state]
            next_max_q = max(next_q_values.values()) if next_q_values else 0
            
            # Update Q-value
            current_q = self.q_table[self.previous_state][self.previous_action]
            new_q = current_q + self.learning_rate * (
                reward + self.discount_factor * next_max_q - current_q
            )
            self.q_table[self.previous_state][self.previous_action] = new_q
            
        except Exception as e:
            self.logger.error(f"Error updating Q-values: {e}")

    def _calculate_reward(self, previous_value, current_value):
        """Calculate reward based on state value change"""
        try:
            state_change = current_value - previous_value
            
            if state_change > 0:
                reward = 2.0 * state_change
            else:
                reward = state_change
                
            if current_value > 0.5 and previous_value > 0.5:
                reward += 0.1
                
            return reward
        except Exception as e:
            self.logger.error(f"Error calculating reward: {e}")
            return 0.0

    def _update_history(self, user_text, response, features, state, action):
        """Update conversation history"""
        try:
            self.conversation_history.append({
                'user_text': user_text,
                'response': response,
                'features': features,
                'state': state,
                'action': action
            })
        except Exception as e:
            self.logger.error(f"Error updating history: {e}")

    def _update_state(self, current_state, action, state_value):
        """Update state tracking"""
        try:
            self.previous_state = current_state
            self.previous_action = action
            self.previous_state_value = state_value
        except Exception as e:
            self.logger.error(f"Error updating state: {e}")