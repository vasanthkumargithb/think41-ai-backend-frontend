import React, { useRef, useEffect } from 'react';
import Message from './Message';
import { useChat } from '../context/ChatContext';

const listStyle = {
  flex: 1,
  padding: '20px',
  overflowY: 'auto',
  display: 'flex',
  flexDirection: 'column',
};

const typingIndicatorStyle = {
    color: '#888',
    fontStyle: 'italic',
    alignSelf: 'flex-start',
    margin: '0 0 10px 15px',
};

const MessageList = () => {
  const { messages, loading } = useChat();
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={listStyle}>
      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
      {loading && <div style={typingIndicatorStyle}>AI is typing...</div>}
      <div ref={endOfMessagesRef} />
    </div>
  );
};

export default MessageList;