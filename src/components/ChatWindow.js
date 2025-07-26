import React from 'react';
import MessageList from './MessageList';
import UserInput from './UserInput';
import { useChat } from '../context/ChatContext';

const windowStyle = {
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  flex: 1,
};

const ChatWindow = () => {
  const { sendMessage, loading } = useChat();

  return (
    <div style={windowStyle}>
      <MessageList />
      <UserInput onSendMessage={sendMessage} disabled={loading} />
    </div>
  );
};

export default ChatWindow;