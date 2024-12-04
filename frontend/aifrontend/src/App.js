// App.js

import './App.css';
import { useState, useEffect, useRef } from 'react';
import { AuthProvider, useAuthInfo, useRedirectFunctions } from "@propelauth/react";
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SavedChats from './SavedChats';
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { Canvas } from '@react-three/fiber';
import BotModel from './BotModel';
import io from 'socket.io-client';

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
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const chatLogRef = useRef(null);
  const socket = useRef(null);
  const utteranceRef = useRef(null); // Ref to store the speech utterance

  useEffect(() => {
    // Initialize the WebSocket connection
    socket.current = io('http://100.110.129.91:5000', {
      transports: ['websocket'],
    });

    // Handle connection events
    socket.current.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    socket.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    socket.current.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    // Handle text responses from the server
    socket.current.on('text_response', (data) => {
      const botResponse = data.text;
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'Bot', text: botResponse },
      ]);

      // Use Text-to-Speech to speak the bot's response
      speak(botResponse);
    });

    // Handle audio responses from the server
    socket.current.on('audio_response', (audioData) => {
      const blob = new Blob([audioData], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      setIsBotSpeaking(true);
      audio.play().catch((error) => {
        console.error('Audio playback error:', error);
      });
      audio.onended = () => {
        setIsBotSpeaking(false);
        URL.revokeObjectURL(url); // Clean up the object URL
      };
    });

    // Handle errors
    socket.current.on('error', (data) => {
      console.error('WebSocket server error:', data.error);
    });

    // Cleanup on component unmount
    return () => {
      if (socket.current) {
        socket.current.disconnect();
      }
    };
  }, []);

  const handleSendMessage = () => {
    if (currentMessage.trim() === '') return;

    const newMessages = [...messages, { sender: 'You', text: currentMessage }];

    setMessages(newMessages);
    setCurrentMessage('');

    if (socket.current && socket.current.connected) {
      socket.current.emit('send_text', { text: currentMessage });
    } else {
      console.error('WebSocket is not connected');
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech Recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setCurrentMessage(transcript);
    };
    recognition.start();
  };

  const speak = (text) => {
    // Use Text-to-Speech to speak the bot's response
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    setIsBotSpeaking(true);
    utterance.onend = () => {
      setIsBotSpeaking(false);
      utteranceRef.current = null;
    };
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsBotSpeaking(false);
      utteranceRef.current = null;
    };
    utteranceRef.current = utterance;
    synth.speak(utterance);
  };

  const stopSpeaking = () => {
    if (utteranceRef.current) {
      window.speechSynthesis.cancel();
      setIsBotSpeaking(false);
      utteranceRef.current = null;
    }
  };

  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages]);

  const saveChat = async () => {
    if (!isLoggedIn || messages.length === 0) return;
    setIsSaving(true);

    try {
      const chatData = {
        userId: user.userId,
        chatId: Date.now().toString(),
        timestamp: new Date().toISOString(),
        messages: messages
      };

      const command = new PutCommand({
        TableName: "ChatHistory",
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
        <Canvas
          className="App-bot-canvas"
          camera={{
            position: [0, 5, 75],
            fov: 50,
          }}
        >
          <ambientLight intensity={0.5} />
          <directionalLight position={[0, 10, 5]} />
          <BotModel isSpeaking={isBotSpeaking} />
        </Canvas>
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
              {isBotSpeaking && (
                <button onClick={stopSpeaking} className="stop-button">🛑 Stop</button>
              )}
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
