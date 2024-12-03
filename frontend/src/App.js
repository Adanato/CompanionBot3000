import './App.css';
import botImage from './bot.jpg';
import { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuthInfo, useRedirectFunctions } from "@propelauth/react";
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SavedChats from './SavedChats';
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";

// Initialize DynamoDB client outside of the component
const client = new DynamoDBClient({ 
  region: "us-east-1",
  credentials: {
    accessKeyId: "AKIA3GMCHGGUVH2T3PFV",
    secretAccessKey: "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"
  }
});

const docClient = DynamoDBDocumentClient.from(client, {
  marshallOptions: {
    convertEmptyValues: true,
    removeUndefinedValues: true,
    convertClassInstanceToMap: true
  }
});

function AuthButton() {
  const { loading, user, isLoggedIn } = useAuthInfo();
  const { redirectToLoginPage, redirectToSignupPage, redirectToAccountPage } = useRedirectFunctions();

  if (loading) {
    return null;
  }

  if (isLoggedIn) {
    return (
      <div className="auth-button">
        <button onClick={redirectToAccountPage} className="auth-btn">
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

function ChatApp() {
  const { user, isLoggedIn } = useAuthInfo();
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const chatLogRef = useRef(null);

  const saveChat = async () => {
    if (!isLoggedIn || messages.length === 0) return;
    setIsSaving(true);

    try {
      const chatData = {
        userId: user.userId,  // String - as per your DynamoDB schema
        chatId: Date.now().toString(),  // String - as per your DynamoDB schema
        timestamp: new Date().toISOString(),
        messages: messages
      };

      const command = new PutCommand({
        TableName: "ChatHistory",  // Updated to match your table name
        Item: chatData
      });

      await docClient.send(command);
      alert("Chat saved successfully!");
    } catch (error) {
      console.error("Error saving chat:", error);
      alert("Failed to save chat: " + error.message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSendMessage = () => {
    if (currentMessage.trim() === '') return;

    const newMessages = [...messages, { sender: 'You', text: currentMessage }];
    const botResponse = `You said: "${currentMessage}"`;
    newMessages.push({ sender: 'Bot', text: botResponse });

    setMessages(newMessages);
    setCurrentMessage('');
    speak(botResponse);
  };

  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages]);

  const startListening = () => {
    const recognition = new window.webkitSpeechRecognition() || new window.SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCurrentMessage(transcript);
    };
    recognition.start();
  };

  const speak = (text) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    synth.speak(utterance);
  };

  return (
    <div className="App">
      <AuthButton />
      <nav className="nav-menu">
        <Link to="/saved-chats" className="nav-link">View Saved Chats</Link>
      </nav>
      <header className="App-header">
        <h1>Companion Bot 3000</h1>
      </header>
      <div className="App-content">
        <img src={botImage} alt="Bot" className="App-bot-image" />
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
          <div className="App-chat-actions">
            <div className="App-chat-input">
              <input
                type="text"
                placeholder="Type a message..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') handleSendMessage();
                }}
              />
              <button onClick={handleSendMessage}>Send</button>
              <button onClick={startListening}>🎤 Speak</button>
            </div>
            {isLoggedIn && messages.length > 0 && (
              <button 
                onClick={saveChat} 
                className="save-chat-btn"
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save Chat'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AppWithRouter() {
  return (
    <BrowserRouter>
      <AuthProvider authUrl="https://4847605902.propelauthtest.com">
        <Routes>
          <Route path="/" element={<ChatApp />} />
          <Route path="/saved-chats" element={<SavedChats />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default AppWithRouter;