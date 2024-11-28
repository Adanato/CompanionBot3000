import './App.css';
import botImage from './bot.jpg';
import { useState } from 'react';

function App() {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');

  const handleSendMessage = () => {
    if (currentMessage.trim() === '') return;

    // Add user's message
    const newMessages = [...messages, { sender: 'You', text: currentMessage }];

    // Simulate bot response
    newMessages.push({ sender: 'Bot', text: `You said: "${currentMessage}"` });

    setMessages(newMessages);
    setCurrentMessage('');
  };

  return (
    <div className="App">
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
          <div className="App-chat-log">
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
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
