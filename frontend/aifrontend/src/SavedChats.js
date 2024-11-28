import { useState, useEffect } from 'react';
import { useAuthInfo } from "@propelauth/react";
import { Link } from 'react-router-dom';
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, QueryCommand, DeleteCommand } from "@aws-sdk/lib-dynamodb";

// Initialize DynamoDB client
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

function ChatModal({ chat, onClose }) {
  if (!chat) return null;
  
  return (
    <div className="chat-modal" onClick={onClose}>
      <div className="chat-modal-content" onClick={e => e.stopPropagation()}>
        <button className="close-modal" onClick={onClose}>×</button>
        <div className="chat-header">
          <h3>{new Date(chat.timestamp).toLocaleString()}</h3>
        </div>
        <div className="saved-chat-messages">
          {chat.messages.map((message, index) => (
            <div
              key={index}
              className={`saved-chat-message ${message.sender.toLowerCase()}`}
            >
              <strong>{message.sender}:</strong> {message.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SavedChats() {
  const { user, isLoggedIn } = useAuthInfo();
  const [savedChats, setSavedChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedChat, setSelectedChat] = useState(null);

  useEffect(() => {
    if (isLoggedIn) {
      fetchSavedChats();
    }
  }, [isLoggedIn]);

  const fetchSavedChats = async () => {
    try {
      const command = new QueryCommand({
        TableName: "ChatHistory",
        KeyConditionExpression: "userId = :userId",
        ExpressionAttributeValues: {
          ":userId": user.userId
        },
        ScanIndexForward: false // This will sort by timestamp in descending order
      });

      const response = await docClient.send(command);
      setSavedChats(response.Items || []);
    } catch (error) {
      console.error("Error fetching saved chats:", error);
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = async (chatId) => {
    if (!window.confirm("Are you sure you want to delete this chat?")) {
      return;
    }

    try {
      const command = new DeleteCommand({
        TableName: "ChatHistory",
        Key: {
          userId: user.userId,
          chatId: chatId
        }
      });

      await docClient.send(command);
      setSavedChats(savedChats.filter(chat => chat.chatId !== chatId));
      if (selectedChat?.chatId === chatId) {
        setSelectedChat(null);
      }
    } catch (error) {
      console.error("Error deleting chat:", error);
      alert("Failed to delete chat");
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="saved-chats">
        <h2>Please sign in to view saved chats</h2>
        <Link to="/" className="back-btn">Back to Chat</Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="saved-chats">
        <h2>Loading saved chats...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      <nav className="nav-menu">
        <Link to="/" className="nav-link">Back to Chat</Link>
      </nav>
      <header className="App-header">
        <h1>Saved Chats</h1>
      </header>
      <div className="saved-chats-content">
        <div className="saved-chats-grid">
          {savedChats.length === 0 ? (
            <p className="empty-state">No saved chats found.</p>
          ) : (
            savedChats.slice(0, 9).map((chat) => (
              <div key={chat.chatId} className="saved-chat-card">
                <div className="saved-chat-header">
                  <h3>{new Date(chat.timestamp).toLocaleString()}</h3>
                </div>
                <div className="saved-chat-messages">
                  {chat.messages.slice(0, 2).map((message, index) => (
                    <div
                      key={index}
                      className={`saved-chat-message ${
                        message.sender.toLowerCase()
                      }`}
                    >
                      <strong>{message.sender}:</strong> {message.text}
                    </div>
                  ))}
                  {chat.messages.length > 2 && (
                    <div className="message-count">
                      +{chat.messages.length - 2} more messages
                    </div>
                  )}
                </div>
                <div className="saved-chat-footer">
                  <button
                    className="view-btn"
                    onClick={() => setSelectedChat(chat)}
                  >
                    View
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => deleteChat(chat.chatId)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      {selectedChat && (
        <ChatModal
          chat={selectedChat}
          onClose={() => setSelectedChat(null)}
        />
      )}
    </div>
  );
}

export default SavedChats;