import './App.css';
import botImage from './bot.jpg';
import { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuthInfo, useRedirectFunctions } from "@propelauth/react";

function AuthButton() {
  const { loading, user, isLoggedIn } = useAuthInfo();
  const { redirectToLoginPage, redirectToSignupPage, redirectToAccountPage } = useRedirectFunctions();

  if (loading) {
    return null;
  }

  if (isLoggedIn) {
    return (
      <div className="auth-button">
        <button 
          onClick={redirectToAccountPage}
          className="auth-btn"
        >
          {user.email}
        </button>
      </div>
    );
  }

  return (
    <div className="auth-button">
      <button onClick={redirectToLoginPage} className="auth-btn">
        Sign In
      </button>
    </div>
  );
}

function App() {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const chatLogRef = useRef(null);

  // Function to handle sending messages
  const handleSendMessage = () => {
    if (currentMessage.trim() === '') return;

    // Add user's message
    const newMessages = [...messages, { sender: 'You', text: currentMessage }];

    // Simulate bot response
    const botResponse = `You said: "${currentMessage}"`;
    newMessages.push({ sender: 'Bot', text: botResponse });

    // Add messages and reset input
    setMessages(newMessages);
    setCurrentMessage('');

    // Speak the bot response
    speak(botResponse);
  };

  // Scroll to the bottom when messages update
  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages]);

  // Speech-to-text using Web Speech API
  const startListening = () => {
    const recognition = new window.webkitSpeechRecognition() || new window.SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCurrentMessage(transcript);
    };
    recognition.start();
  };

  // Text-to-speech using Web Speech API
  const speak = (text) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    synth.speak(utterance);
  };

  return (
    <div className="App">
      <AuthButton />
      <header className="App-header">
        <h1>Companion Bot 3000</h1>
      </header>
      <div className="App-content">
        <img
          src={botImage}
          alt="Bot"
          className="App-bot-image"
        />
        <div className="App-chat">
          <div className="App-chat-log" ref={chatLogRef}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`App-chat-message ${
                  message.sender === 'You' ? 'user-message' : 'bot-message'
                }`}
              >
                <strong>{message.sender}:</strong> {message.text}
              </div>
            ))}
          </div>
          <div className="App-chat-input">
            <input
              type="text"
              placeholder="Type a message..."
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
            />
            <button onClick={handleSendMessage}>Send</button>
            <button onClick={startListening}>🎤 Speak</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Wrap the exported app with PropelAuth's AuthProvider
function AppWithAuth() {
  return (
    <AuthProvider authUrl="https://4847605902.propelauthtest.com">
      <App />
    </AuthProvider>
  );
}

export default AppWithAuth;