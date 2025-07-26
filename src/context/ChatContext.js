import React, { createContext, useState, useContext } from 'react';
import { v4 as uuidv4 } from 'uuid';

const ChatContext = createContext();

export const useChat = () => useContext(ChatContext);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // Function to add a new message and simulate AI response
  const sendMessage = (text) => {
    const userMessage = { id: uuidv4(), text, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = { id: uuidv4(), text: `This is the AI's response to: "${text}"`, sender: 'ai' };
      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1500);
  };

  // Function to save the current chat and start a new one
  const startNewChat = () => {
    if (messages.length > 0) {
      setHistory(prev => [{ id: uuidv4(), messages: messages }, ...prev]);
    }
    setMessages([]);
  };

  // Function to load a past conversation
  const loadChatHistory = (chat) => {
    setMessages(chat.messages);
  };

  const value = {
    messages,
    loading,
    history,
    sendMessage,
    startNewChat,
    loadChatHistory,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};