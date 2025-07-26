import React from 'react';

const messageStyle = {
  padding: '10px 15px',
  borderRadius: '20px',
  marginBottom: '10px',
  maxWidth: '70%',
  wordWrap: 'break-word',
};

const userStyle = {
  ...messageStyle,
  backgroundColor: '#007bff',
  color: 'white',
  alignSelf: 'flex-end',
};

const aiStyle = {
  ...messageStyle,
  backgroundColor: '#e9e9eb',
  color: 'black',
  alignSelf: 'flex-start',
};

const Message = ({ message }) => {
  const isUser = message.sender === 'user';
  return (
    <div style={isUser ? userStyle : aiStyle}>
      {message.text}
    </div>
  );
};

export default Message;